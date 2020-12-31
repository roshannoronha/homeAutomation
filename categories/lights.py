from qhue import Bridge
import math
from pathlib import Path

def getHueInfo():

    filePath = Path("D:\\Documents\\homeAutomation\\categories\\lighting\\hueInfo.txt")

    f = open(filePath, "r")
    data = f.readlines()
    f.close()

    #info = data.split(",")
    bridgeInfo = data[0].split(":")
    userInfo = data[1].split(":")

    bridgeIP = bridgeInfo[1].strip("\n").strip()
    userID = userInfo[1].strip("\n").strip()

    return bridgeIP, userID

def getBridge():
    '''Returns a bridge object and the number of light groups'''

    bridgeIP, userID = getHueInfo()
    
    b = Bridge(bridgeIP, userID)
    groupNums = b.groups().keys()

    return (b, groupNums)

def convertBrightLevel(brightPercentage):
    '''Converts a percentage to the corresponding brightness level'''

    return math.ceil((brightPercentage/100) * 255)

def lightsOnOff(bridge, groupNums, state):
    '''Turns lights in a group on or off'''
    
    for num in groupNums:
        bridge.groups[num].action(on=state)

def setBrightness(bridge, groupNums, sliderValue):
    '''Sets the brightness of a light group'''

    brightLevel = convertBrightLevel(sliderValue)

    if brightLevel == 0:
        lightsOnOff(bridge, groupNums, False)
    else:
        lightsOnOff(bridge, groupNums, True)

        for num in groupNums:
            bridge.groups[num].action(bri=brightLevel)

def setColor(bridge, groupNums, colorValue):
    '''Sets the color of a light group'''

    for num in groupNums:
        bridge.groups[num].action(ct=colorValue)


getHueInfo()







