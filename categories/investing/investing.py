	
from datetime import datetime
from numpy.lib.histograms import histogram
from pandas.core.algorithms import mode
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import pyotp
from pathlib import Path
import json
import yfinance as yf
from forex_python.converter import CurrencyRates

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def generateQRURL():

    '''Given a authenticator key generates QR code info that can be passed to an authenticator app'''

    #received from wealthica
    filePath = Path("C:\\homeAutomation\\categories\\investing\\data\\wealthicaInfo.txt")
    with open(filePath, "r") as file:
        data = file.readlines()

    key = data[0].replace("\n", "")
    print(pyotp.totp.TOTP(key).provisioning_uri(name='roshananoronha@gmail.com', issuer_name= 'homeAutomation'))

def getWealthicaLoginInfo():

    '''Returns info to login to wealthica site'''

    filePath = Path("C:\\homeAutomation\\categories\\investing\\data\\wealthicaInfo.txt")
    with open(filePath, "r") as file:
        data = file.readlines()

    key = data[0].replace("\n", "")
    url = data[1].replace("\n", "")
    userName = data[2].replace("\n", "")
    password = data[3].replace("\n", "")
    
    totp = pyotp.TOTP(key)

    return (totp.now(), url, userName, password)

def getWealthicaData():

    '''Gets data from Wealthica and saves it to a json file'''

    auth, url, userName, password = getWealthicaLoginInfo()

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    #chrome_options.add_argument("--headless")
    browser = webdriver.Chrome(executable_path="C:/Program Files/chromedriver_win32/chromedriver.exe", options= chrome_options) 

    browser.get(url)
    WebDriverWait(browser, 30)
    browser.find_element_by_name("email").send_keys(userName)
    browser.find_element_by_name("password").send_keys(password)
    browser.find_element_by_class_name("btn-login").click()

    WebDriverWait(browser, 30)
    time.sleep(2)
    browser.find_element_by_class_name("auth__input").send_keys(auth)
    browser.find_element_by_class_name("btn-verify").click()

    WebDriverWait(browser, 30)
    time.sleep(5)

    browser.switch_to.frame("iFrameResizer0")

    ##Get overview data
    overviewValues = browser.find_elements_by_xpath("//div[@class='no-wrap value private-mode-hidden']")
    overviewValuesCategories = ["Networth As Of Today", "Financial Institutions", "Real Estate Properties", "Alternative Investments", "Other Assets"]

    overviewValuesDict = {}

    for counter in range(0, len(overviewValuesCategories)):
        overviewValuesDict[overviewValuesCategories[counter]] = overviewValues[counter].text


    ##Get data from each account
    currentAccounts = {}

    #click all drop down icons first 
    #This ensures that accounts in each category are read
    dropdowns = browser.find_elements_by_class_name('dropdown')
    for dropdownArrow in dropdowns:
        dropdownArrow.click()

    accounts = browser.find_elements_by_class_name('item-name')
    values = browser.find_elements_by_xpath("//div[@class='no-wrap private-mode-hidden completely']")

    returnedAccounts = []
    returnedValues = []

    for account in accounts:
        text = account.text
        returnedAccounts.append(text.replace("\n", ""))

    for value in values:
        text = value.text
        returnedValues.append(text.replace("\n", ""))

    accountTypes = ["High Interest Savings Account", "RSP Savings Account", "RRSP", "TSFA"]

    #save bank name in currentAccounts and ignore the names in accountTypes
    for account in list(dict.fromkeys(returnedAccounts)):
        if not account in accountTypes:
            currentAccounts[account] = {}

    #get the indices of matching accountTypes
    matchingAccountsTypesIndices = []
    for account in accountTypes:
        matchingAccountsTypesIndices.append(returnedAccounts.index(account))

    #using the matchingAccountsTypesIndices the value before the index is the bank. 
    #the index is the type of account
    for index in matchingAccountsTypesIndices:
        currentAccounts[returnedAccounts[index - 1]][returnedAccounts[index]] = None

    #remove duplicate values
    currentValues = list(dict.fromkeys(returnedValues))
    valueCounter = 0

    #add the values to the appropriate account
    for account in currentAccounts.keys():

        if len(currentAccounts[account].keys()) > 0:
            for accountType in currentAccounts[account].keys():
                currentAccounts[account][accountType] = currentValues[valueCounter]
                valueCounter = valueCounter + 1
        else:
            currentAccounts[account] = currentValues[valueCounter]
            valueCounter = valueCounter + 1

    wealthicaDict = {'overview': overviewValuesDict, 'accounts': currentAccounts}
    with open("C:\\homeAutomation\\categories\\investing\\data\\wealthicaData.json", 'w') as file:
        json.dump(wealthicaDict, file)


def getABCLStockHistory():

    '''Gets AbCellera stock data from Yahoo finance'''
    #current stocks purchased
    abcl = yf.Ticker('ABCL')

    sixMonthHistory = abcl.history(period='6mo')
    
    return sixMonthHistory

def currentABCLStockValue(history):

    '''Calculates current value of AbCellera stock based on the number of shares'''

    currentPrice = history.iloc[len(history) - 1]['Close']
    currentNetValueUSD = round(currentPrice * 100, 2)
    
    currentNetValueCAD = round(CurrencyRates().convert('USD', 'CAD', currentNetValueUSD), 2)

    currentDate = str(history.iloc[len(history) - 1].name).split(" ")[0]
    
    return currentNetValueUSD, currentNetValueCAD, currentDate


def getCurrentStockInfo():

    sixMonthHistory = getABCLStockHistory()
    currentNetValueUSD, currentNetValueCAD, currentDate = currentABCLStockValue(sixMonthHistory)

    stockInfoDict = {
        "currentDate":currentDate,
        "currentNetValueUSD": currentNetValueUSD,
        "currentNetValueCAD": currentNetValueCAD,
        "sixMonthHistory": sixMonthHistory.to_json()
    }

    with open("C:\\homeAutomation\\categories\\investing\\data\\stockInfo.json", 'w') as file:
        json.dump(stockInfoDict, file)
    

def updateCurrentFinancialInfo():
    getCurrentStockInfo()
    getWealthicaData()

    with open("C:\\homeAutomation\\categories\\investing\\data\\wealthicaData.json", 'r') as file:
        wealthicaData = json.load(file)

    with open("C:\\homeAutomation\\categories\\investing\\data\\stockInfo.json", 'r') as file:
        stockInfo = json.load(file)

    wealthicaCurrent = wealthicaData['overview']['Networth As Of Today'].replace("$", "").replace(",", "")
    stockCurrent = stockInfo['currentNetValueCAD']
    currentNetworth = (float(wealthicaCurrent) + float(stockCurrent))
    updateNetworthHistory(currentNetworth)


def getCurrentFinancialInfo():

    with open("C:\\homeAutomation\\categories\\investing\\data\\wealthicaData.json", 'r') as file:
        wealthicaData = json.load(file)

    with open("C:\\homeAutomation\\categories\\investing\\data\\stockInfo.json", 'r') as file:
        stockInfo = json.load(file)
      
    #overview
    wealthicaCurrent = wealthicaData['overview']['Networth As Of Today'].replace("$", "").replace(",", "")
    stockCurrent = stockInfo['currentNetValueCAD']
    currentNetworth = "${:,.2f}".format(float(wealthicaCurrent) + float(stockCurrent))


    wealthicaData['overview'].pop('Networth As Of Today')
    wealthicaData['overview'].pop('Real Estate Properties')
    wealthicaData['overview'].pop('Other Assets')

    overview = {}
    overview["Networth"] = currentNetworth
    overview.update(wealthicaData['overview'])
    
    #holdings
    currentStockCAD = "${:,.2f}".format(stockInfo['currentNetValueCAD'])
    currentStockUSD = "${:,.2f}".format(stockInfo['currentNetValueUSD'])
    holdings = wealthicaData['accounts']
    holdings['AbCellera Stock'] = {'CAD': currentStockCAD, 'USD': currentStockUSD}

    return overview, holdings

def stockDataViz():

    with open("C:\\homeAutomation\\categories\\investing\\data\\stockInfo.json", 'r') as file:
        stockInfo = json.load(file)

    #six month stock history
    sixMonthHistory = json.loads(stockInfo["sixMonthHistory"])

    openData = sixMonthHistory['Open']
    dates = []
    openValues = []

    closeData = sixMonthHistory['Close']
    closeValues = []

    lowData = sixMonthHistory['Low']
    lowValues = []

    highData = sixMonthHistory['High']
    highValues = []

    for timestamp in openData.keys():
        
        dates.append(datetime.utcfromtimestamp(int(timestamp)/1000).strftime('%Y-%m-%d'))
        openValues.append(openData[timestamp])
        closeValues.append(closeData[timestamp])
        lowValues.append(lowData[timestamp])
        highValues.append(highData[timestamp])
        

    abclData = pd.DataFrame(
        {
            "Dates": dates,
            'Open': openValues,
            'Low': lowValues,
            'Close': closeValues,
            'High': highValues
        }
    )

    fig = go.Figure(data=[go.Candlestick(
        x= abclData['Dates'],
        open= abclData['Open'],
        high= abclData['High'],
        low= abclData['Low'],
        close= abclData['Close']),  
    ])

    fig.update_layout(

        title = '<b>AbCellera Biologics Inc. (ABCL)</b>',
        title_font_color="white",

        xaxis_rangeslider_visible=False,
        height = 700,
        clickmode= "none",
        #dragmode = False,

        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',

        yaxis=dict(
           
            #titlefont_size=16,
            #tickfont_size=14,
            color = "white"
        ),

        xaxis=dict(
            
            #titlefont_size=16,
            #tickfont_size=14,
            color = "white"
        ),
    )

    return fig


def updateNetworthHistory(currentNetworth):

    with open("C:\\homeAutomation\\categories\\investing\\data\\networthHistory.json", 'a') as file:
        file.write(f"{datetime.now().date()} {currentNetworth}\n")


def networthHistoryViz():
    with open("C:\\homeAutomation\\categories\\investing\\data\\networthHistory.json", 'r') as file:
        data = file.readlines()
    
    networthData = pd.DataFrame()
    for value in data:
        vals = value.replace("\n", "").split(" ")
        networthData = networthData.append(pd.DataFrame({"Date": vals[0], "Value": [vals[1]]}, columns= ['Date', 'Value']), ignore_index= True)
    
    #remove rows that have duplicate dates. One remains
    networthData = networthData.drop_duplicates(subset=["Date"])
    print(networthData['Date'])

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=list(networthData['Date']), y=list(networthData['Value']), mode='lines+markers', line=dict(color='#28a745', width=4)))
    fig.update_traces(marker=dict(size=20))

    fig.update_layout(
        #showlegend=False,
        title = '<b>NETWORTH HISTORY</b>',
        title_font_color="white",

        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',

        yaxis=dict(
            title = 'NETWORTH VALUE',
            color = "white",
        ),

        xaxis=dict(
            title = "DATE",
            color = "white",
        ),
    )

    return fig



#networthHistoryViz()
#pdateCurrentFinancialInfo()












