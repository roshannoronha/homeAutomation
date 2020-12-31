from categories.googleCalendar import storeCalendarData
from pathlib import Path
import os

#get calendar data
#filePath = Path("D:/Documents/homeAutomation/categories/calendar/calendarInfo.txt")
#storeCalendarData(filePath)

#start dashboard
dashboardPath = Path("D:/Documents/homeAutomation/dashboard.py")
os.system(f'python {dashboardPath}')
