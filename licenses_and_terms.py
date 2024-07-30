#!/usr/bin/env python3

import os
import sys
import json
import subprocess
import csv
from datetime import datetime
from pprint import pprint
import logging
import time

try:
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    from dotenv import load_dotenv
except ImportError:
    missing_packages = []
    try:
        import requests
    except ImportError:
        missing_packages.append('requests')

    try:
        from requests.packages.urllib3.exceptions import InsecureRequestWarning
    except ImportError:
        if 'requests' not in missing_packages:
            missing_packages.append('requests')

    try:
        from dotenv import load_dotenv
    except ImportError:
        missing_packages.append('python-dotenv')

    if missing_packages:
        install = input(f"The following packages are missing: {missing_packages}. Do you want to install them? Yes/no (default is Yes): ").strip().lower()
        if install in ('', 'y', 'yes'):
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_packages)
                import requests
                from requests.packages.urllib3.exceptions import InsecureRequestWarning
                from dotenv import load_dotenv
            except subprocess.CalledProcessError as e:
                logging.error(f"Failed to install packages: {e}")
                sys.exit()
        elif install in ('n', 'no'):
            logging.info("Installation aborted by the user.")
            sys.exit()
        else:
            logging.info("Invalid input. Installation aborted.")
            sys.exit()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Check for .env file
if os.path.exists('.env'):
    print("Detected .env file.")
    load_dotenv()
else:
    print(".env file not detected. You will be prompted to enter environment variables.")

# Load environment variables
BASEURL = os.getenv('BASEURL')
API_TOKEN = os.getenv('API_TOKEN')

if not BASEURL or not API_TOKEN:
    BASEURL = input("Enter BASEURL: ")
    API_TOKEN = input("Enter API_TOKEN: ")
    with open('.env', 'w') as f:
        f.write(f"BASEURL={BASEURL}\n")
        f.write(f"API_TOKEN={API_TOKEN}\n")

AUTHURL = f"{BASEURL}/api/tokens/authenticate"
today_date = datetime.now()
date_time = today_date.strftime('%Y-%m-%d %H:%M')
http_method = "GET"
payload = {}
output = {
    'logs': [],
    'licenses': []
}

def log(entry):
    '''
    Append new log entries
    '''
    output['logs'].append(entry)

    with open("logfile.json", "w") as outfile:
        json.dump(output, outfile, indent=4)

def http_error_check(url, headers, code, response):
    '''
    Function to check the HTTP status code.
    '''
    if code == 200:
        return

    if code > 399:
        logging.error(f"Unable to pull info from endpoint. URL: {url}, HTTP error: {code}")
        log(f"{date_time} URL: {url} HEADERS: {headers} HTTP error: {code}")
        log(response.text)
        sys.exit()

    else:
        raise Exception("Error while getting data.", code)

def get_auth():
    '''
    Function to authenticate to the BD API and grab the bearer token and csrf token.
    '''
    url = AUTHURL
    headers = {
        'Accept': 'application/vnd.blackducksoftware.user-4+json',
        'Authorization': 'token ' + API_TOKEN
    }

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    try:
        response = requests_retry_session().post(url, headers=headers, data=payload, verify=False, timeout=15)
        code = response.status_code
        http_error_check(url, headers, code, response)

        if code == 200:
            global bearerToken, csrfToken
            bearerToken = response.json()['bearerToken']
            csrfToken = response.headers['X-CSRF-TOKEN']

    except requests.exceptions.RequestException as e:
        logging.error(f"Authentication failed: {e}")
        sys.exit()

def get_url(http_method, url, headers, payload):
    '''
    Function to enumerate data from a URL or API endpoint.
    '''
    try:
        response = requests_retry_session().request(http_method, url, headers=headers, data=payload, verify=False, timeout=15)
        code = response.status_code
        http_error_check(url, headers, code, response)

        if code == 200:
            return response.json()

    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        sys.exit()

def get_licenses():
    '''
    Function to enumerate a list of licenses.
    '''
    print("Enumerating licenses and their terms. This process may take about 10-15 minutes.")
    print("At the end, you will have the option to save the results in either CSV or JSON format.")
    input("Press Enter to continue...")
    
    url = f'{BASEURL}/api/license-dashboard?limit=3000'
    logging.info(f"URL: {url}")
    headers = {
        'Accept': 'application/vnd.blackducksoftware.bill-of-materials-6+json',
        'Authorization': 'bearer ' + bearerToken,
        'X-CSRF-TOKEN': csrfToken
    }
    results = get_url(http_method, url, headers, payload)
    pprint(results)

    try:
        for license in results['items']:
            name = license['name']
            href = license['_meta']['href']
            logging.info(f"Enumerating license: {name}")
            license_terms = get_license_terms(href)
            output['licenses'].append({
                'name': name,
                'terms': license_terms
            })

    except KeyError:
        logging.error("Exception getting licenses")

def get_license_terms(href):
    '''
    Function to enumerate license terms from a list of licenses.
    '''
    url = href + "/license-terms"
    headers = {
        'Accept': 'application/vnd.blackducksoftware.component-detail-5+json',
        'Authorization': 'bearer ' + bearerToken,
        'X-CSRF-TOKEN': csrfToken
    }
    results = get_url(http_method, url, headers, payload)
    terms = []

    try:
        for license_terms in results['items']:
            logging.info(f"License Term: {license_terms['name']}")
            terms.append({
                'name': license_terms['name'],
                'responsibility': license_terms['responsibility'],
                'description': license_terms['description']
            })
    except KeyError:
        logging.error("Exception getting license terms")

    return terms

def export_results():
    '''
    Function to export results to CSV or JSON based on user selection.
    '''
    save_choice = input("Do you want to save the results? (Yes/no, default is Yes): ").strip().lower()
    if save_choice not in ('', 'y', 'yes'):
        logging.info("Results not saved.")
        return

    choice = input("Do you want to export the results to CSV or JSON? (default is JSON): ").strip().lower()
    if choice in ('', 'json'):
        with open('results.json', 'w') as outfile:
            json.dump(output, outfile, indent=4)
        logging.info("Results exported to results.json")
    elif choice == 'csv':
        with open('results.csv', 'w', newline='') as csvfile:
            fieldnames = ['License Name', 'Term Name', 'Responsibility', 'Description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for license in output['licenses']:
                for term in license['terms']:
                    writer.writerow({
                        'License Name': license['name'],
                        'Term Name': term['name'],
                        'Responsibility': term['responsibility'],
                        'Description': term['description']
                    })
        logging.info("Results exported to results.csv")
    else:
        logging.info("Invalid input. Results not exported.")

def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = requests.packages.urllib3.util.retry.Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = requests.adapters.HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def main():
    '''
    Main function
    '''
    print("You will have the option to save the results in either CSV or JSON format at the end.")
    input("Press Enter to continue...")
    get_auth()
    get_licenses()
    export_results()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Control-C detected, exiting.")
        sys.exit()
