# Thomas Robert
# 06/30/2023
# https://github.com/trasbd/getSchedule
# 
# Gets schedule from SixFlags.Team and imports into Google Calendar

# pip install selenium
# pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

import secrects

from datetime import datetime
import os.path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


options = webdriver.ChromeOptions();

#Disables images so it loads faster
options.add_experimental_option("prefs", {'profile.managed_default_content_settings.images': 2})

options.add_argument("headless")
options.add_argument("--no-sandbox") # required for docker run

browser = webdriver.Chrome(options=options)

browser.get('http://sixflags.team')
assert 'Six Flags Team' in browser.title

browser.find_element(By.ID, 'alogin2').click()

browser.find_element(By.ID, 'txtCompany').send_keys(secrects.company)
browser.find_element(By.ID, 'txtuserid').send_keys(secrects.eid)
browser.find_element(By.ID, 'txtpwd').send_keys(secrects.pin)

browser.find_element(By.ID, 'btnlogin1').click()

browser.get('https://sixflags.team/em/default/getschedule/')

scheduleRows = browser.find_elements(By.TAG_NAME,'tr')

shifts = []

for row in scheduleRows[1:]:
    rowTD = row.find_elements(By.TAG_NAME,'td')
    if not ("(Not Scheduled)" in rowTD[2].text):
        scheduleId    = row.get_attribute("rowid")
        shiftDate     = datetime.strptime(rowTD[1].text, "%m/%d/%Y %a")
        shiftLocation = rowTD[3].text
        shiftTimes    = rowTD[5].text.split(" - ")
        shiftStart    = datetime.combine(shiftDate, datetime.strptime(shiftTimes[0], "%I:%M %p").time())
        shiftEnd      = datetime.combine(shiftDate, datetime.strptime(shiftTimes[1], "%I:%M %p").time())

        # print(scheduleId)
        # print(shiftStart)
        # print(shiftEnd)
        # print()

        shiftData = {
            'summary': shiftLocation,
            'location': "G87C+23 Pacific, Missouri",
            'description': scheduleId,
            'start': {
                'dateTime': shiftStart.isoformat(),
                'timeZone': 'US/Central'
            },
            'end': {
                'dateTime': shiftEnd.isoformat(),
                'timeZone': 'US/Central'
            },
            # 'attendees': [
            #     {'email': ''},
            #     {'email': ''},
            # ],
            'reminders': {
                'useDefault': False,
                'overrides': [
                {'method': 'popup', 'minutes': 75}
                ]
            }
        }

        #print(shiftData)
        #print()

        shifts.append(shiftData)

browser.quit()

#print(shifts)

# Need Google Cloud Credentials
# https://developers.google.com/calendar/api/quickstart/python

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

calendarId = secrects.calendarId

creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

try:
    service = build('calendar', 'v3', credentials=creds)

    dt = datetime.today()
    now = datetime.combine(dt, datetime.min.time()).isoformat() + 'Z'

    #now = datetime.today().isoformat() + 'Z'  # 'Z' indicates UTC time
    events_result = service.events().list(calendarId=calendarId, timeMin=now,
                                                singleEvents=True,
                                                orderBy='startTime').execute()
    events = events_result.get('items', [])
    for event in events:
        service.events().delete(calendarId=calendarId, eventId=event['id']).execute()
    print()

    # Call the Calendar API
    for shift in shifts:
        event = service.events().insert(calendarId=calendarId, body=shift).execute()
        print('Event created: %s' % (event.get('htmlLink')))


except HttpError as error:
    print('An error occurred: %s' % error)
