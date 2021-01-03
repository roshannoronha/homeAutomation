from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pandas as pd
from pathlib import Path

def authorize():
    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'categories/calendar/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)


    return creds

def getCalendarInfo(creds):

    '''Get info from google calendar'''

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    return events

def writeCalendarToFile(calEvents, filePath):

    f = open(filePath, "a")

    for index, row in calEvents.iterrows():
        #print(row)
        f.write(f'{row["Date"]} \t {row["Event"]} \n')
    
    f.close()


def storeCalendarData(filePath):

    open(filePath, 'w').close()

    eventsInfo = getCalendarInfo(authorize())
    eventsTable = pd.DataFrame()

    if not eventsInfo:
        return('No upcoming events found.')
    
    for event in eventsInfo:
        #start = event['start'].get('date', event['start'].get('date'))
        eventDateTime = event['start'].get('dateTime')
        if eventDateTime != None:
            eventDate = eventDateTime[0:10]
            eventName = event['summary']
            eventsTable = eventsTable.append({"Date":eventDate, "Event": eventName}, ignore_index=True)

    
    writeCalendarToFile(eventsTable, filePath)

def getCalendarEvents(filePath):
    '''Read calendar events from text file and return it as a pandas dataframe'''
    eventsDataframe = pd.read_table(filePath, names= ["Date", "Event"], sep = "\t")

    return eventsDataframe 




