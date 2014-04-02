Purpose
=======
The calendar emails application is intended to scrape all emails associated with any events contained in Google calendars. An example would be an organization who wants to scrape all emails associated with any events in the past, for use with a marketing campaign, newsletter, etc.

Execution
=========
1. client_secrets.json file: contains auth permissions associated with a Google account which owns the API calls for the application. To register a new API account, go to the Google Developers Console here: https://console.developers.google.com/project, then create a new project, turn the calendar APIs on, create a new OAuth client ID, and pop that information into client_secrets.json.

2. master_list.csv: contains all known emails. The calendar emails application compares all emails in your events against a master list and returns the difference. If you want all emails regardless, create a blank csv file named 'master_list.csv'.

3. calendars_to_process.csv: contains specific calendar IDs to process. Usefull if you have an organization that conatins lots of calendars and you only want to process a few. Place the emails in new rows in col1.

4. Run the program with '$ python calendar_emails.py'. Select the Google account you want to process calendars for.

5. Emails and names that do not exist in master_list.csv are written to a csv file called new_contacts.csv. This file is overwritten every time the program runs.

6. Enjoy.

Documentation
=============
https://developers.google.com/google-apps/calendar/

Legal
=====
Not responsible for anything
