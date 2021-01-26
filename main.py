from categories.calendar.googleCalendar import storeCalendarData
from categories.investing.investing import updateCurrentFinancialInfo
from pathlib import Path
import os
import webbrowser


print('FETCHING CALENDAR DATA')
filePath = Path("C:\homeAutomation\categories\calendar\calendarInfo.txt")
storeCalendarData(filePath)

print('FETCHING FINANCIAL INFORMATION')
updateCurrentFinancialInfo()

#start dashboard
dashboardPath = Path("C:\\homeAutomation\\dashboard.py")
webbrowser.open('http://127.0.0.1:8050/')
os.system(f'python {dashboardPath}')


