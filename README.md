This is a Python script that:

- analyzes the system to see what (if any) Python packages the script needs for execution are missing; prompts for install.
- prompts for a Black Duck server URL and an API Token Key, creates a .env file and stores the credentials there.
- upon restart or execution after a URL and Token Key have been added, pulls the creds from the .env file.
- provides a notification that the user can save to .csv or .json after all of the licenses and terms have been enumerated from the Black Duck server's API.
- enumerates licenses and then associated license terms (key fields only; not everything)
- saves to either .csv or .json
