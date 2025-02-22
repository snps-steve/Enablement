# License Enumeration Script

## Overview

- Analyzes the system to see what (if any) Python packages the script needs for execution are missing; prompts for installation.
- Authenticates with the Black Duck API
- Retrieves Black Duck license data and associated license terms and allows exporting results in either the JSON or CSV format.

The script requires configuration of API details, which can be provided via a `.env` file or entered interactively.

## Features

- **Authenticate**: Authenticates to the Black Duck API using a provided token.
- **Retrieve Licenses**: Fetches a list of licenses from the Black Duck API.
- **License Terms**: Enumerates terms for each license.
- **Export Results**: Allows exporting the results to JSON or CSV formats.

## Requirements

- Python 3.x
- `requests` library
- `python-dotenv` library (optional for environment management)

You can install the required Python packages using pip or let the script install them for you:

```bash
pip install requests python-dotenv
```

## Installation

Clone this repository:

```bash
git clone https://github.com/snps-steve/license-and-license-terms.git
```

Navigate to the project directory:

```bash
cd license-and-license-terms
```

## Usage

Set up your environment variables in a `.env` file or let the script prompt you for the required information. 

- prompts for a Black Duck server URL, and an API Token Key, creates a .env file, and stores the credentials there.
- upon restart or execution after a URL and Token Key have been added, pull the credentials from the .env file.
- provides a notification that the user can save to .csv or .json after all of the licenses and terms have been enumerated from the Black Duck server's API.
- enumerates licenses and then associated license terms (key fields only; not everything)
- saves to either .csv or .json

Run the script:

```bash
python licenses_and_terms.py
```

## Configuration

During the first execution of the script, you will be prompted for `BASEURL` and `API_TOKEN`. These fields will then be stored in a `.env` file for future use.

If a `.env` file is detected, the script will use the existing configuration or prompt you to enter new information if required.

## Example

If the `.env` file is detected, you will be prompted to either use the existing `BASEURL` and `API_TOKEN` or enter new values. The script will then proceed to authenticate and fetch license data.

## License

This project is licensed under the MIT License.

## Contributing

If you would like to contribute to this project, please fork the repository and submit a pull request.

## Contact

For any questions or issues, please contact [Steve R. Smith](mailto:ssmith@blackduck.com).
