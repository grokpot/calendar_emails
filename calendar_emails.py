# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Command-line skeleton application for Calendar API.
Usage:
  $ python calendar_emails.py

You can also get help on all the command-line flags the program understands
by running:

  $ python calendar_emails.py --help

version: 4

"""

import argparse
from datetime import datetime
import httplib2
import os
import sys
import csv
from apiclient import discovery
from oauth2client import file
from oauth2client import client
from oauth2client import tools

# Parser for command-line arguments.
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[tools.argparser])


# CLIENT_SECRETS is name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret. You can see the Client ID
# and Client secret on the APIs page in the Cloud Console:
# <https://cloud.google.com/console#/project/752975147425/apiui>
CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')

# Set up a Flow object to be used for authentication.
# Add one or more of the following scopes. PLEASE ONLY ADD THE SCOPES YOU
# NEED. For more information on using scopes please see
# <https://developers.google.com/+/best-practices>.
FLOW = client.flow_from_clientsecrets(CLIENT_SECRETS,
  scope=[
      'https://www.googleapis.com/auth/calendar',
      'https://www.googleapis.com/auth/calendar.readonly',
    ],
    message=tools.message_if_missing(CLIENT_SECRETS))


def main(argv):
    # Parse the command-line flags.
    flags = parser.parse_args(argv[1:])

    # If the credentials don't exist or are invalid run through the native client
    # flow. The Storage object will ensure that if successful the good
    # credentials will get written back to the file.
    storage = file.Storage('sample.dat')
    # credentials = storage.get()   # Uncomment this for persistent auth
    # if credentials is None or credentials.invalid:
    credentials = tools.run_flow(FLOW, storage, flags)

    # Create an httplib2.Http object to handle our HTTP requests and authorize it
    # with our good Credentials.
    http = httplib2.Http()
    http = credentials.authorize(http)

    # Construct the service object for the interacting with the Calendar API.
    service = discovery.build('calendar', 'v3', http=http)

    # Get the date to search from
    date_input = raw_input("Enter a date to search from. If none provided, all events will be processed. EX: 01/22/2014: ").split('/')
    date = datetime(int(date_input[2]), int(date_input[0]), int(date_input[1])).isoformat()+'z' if date_input != [''] else None

    try:
        master_email_set = set()
        # Read in master email list and create a set
        with open('master_list.csv', 'rU') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                master_email_set.add(row[1])

        calendars_to_process = []
        try:
            # Read in calendars to process - if using this at an organization, you might only want to run through certain cals
            with open('calendars_to_process.csv', 'rU') as csvfile:
                reader = csv.reader(csvfile, delimiter=',')
                for row in reader:
                   calendars_to_process.append(row[0])
        except IOError:
            pass

        attendees = {} # Create a dict which contains email:name pairs
        new_email_set = set() # Create a new email set, for set difference against master list
        num_events = 0
        calendars = service.calendarList().list().execute()['items'] # Read in all calendars for user
        if calendars_to_process:
            calendars = (cal for cal in calendars if cal['id'] in calendars_to_process)    # Generator Expression to only iterate through our needed calendars, if the document exists
        for calendar in calendars:
            print "Processing calendar %s" % calendar['summary']
            page_token = None
            # Read all events per calendar
            while True:
                events = service.events().list(calendarId=calendar['id'], pageToken=page_token, timeMin=date).execute()
                for event in events['items']:
                    num_events += 1
                    # Add email:name pairs to the email dict and emails to the set
                    for attendee in event.get('attendees', []):
                        attendees[attendee.get('email')] = attendee.get('displayName')
                        new_email_set.add(attendee.get('email'))
                    page_token = events.get('nextPageToken')
                if not page_token:
                    break
        print "%s events were processed" % num_events
        email_difference = new_email_set.difference(master_email_set)   # We only want new emails
        new_contacts = []
        for email in email_difference:  # Need to get the email:name pairs for new contacts
            new_contacts.append([attendees[email], email])
        print "%s new contacts recovered" % len(new_contacts)
        print new_contacts

        # Write new contacts to a CSV
        with open('new_contacts.csv', 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            for contact in new_contacts:
                writer.writerow([unicode(contact[0]).encode("utf-8"), unicode(contact[1]).encode("utf-8")]) # Encoding protection against weird characters and None

    except IOError:
        print "Make sure you have a master emails list named 'master_list.csv' in the same directory"
    except client.AccessTokenRefreshError:
        print ("The credentials have been revoked or expired, please re-run"
        "the application to re-authorize")
    except Exception as e:
        print e.message


# For more information on the Calendar API you can visit:
#
#   https://developers.google.com/google-apps/calendar/firstapp
#
# For more information on the Calendar API Python library surface you
# can visit:
#
#   https://developers.google.com/resources/api-libraries/documentation/calendar/v3/python/latest/
#
# For information on the Python Client Library visit:
#
#   https://developers.google.com/api-client-library/python/start/get_started
if __name__ == '__main__':
  main(sys.argv)
