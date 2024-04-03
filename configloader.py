import configparser
import os

def loadConfigFile(filename):
    parser = configparser.ConfigParser()
    if not os.path.exists(filename):
        print("Config file not found!")
        if filename == 'config.cfg':
            print("Writing default config...")
            writeDefaultConfig()
            return loadConfigFile('config.cfg')

    parser.read(filename)
    
    configList = dict()
    
    checkinOptions = parser['checkin']
    
    configList['universalQueuePolicy'] = int(checkinOptions.get('universalQueuePolicy', '1'))
    configList['nCoachCheckin'] = int(checkinOptions.get('coachCheckin', '3'))
    configList['nBusiCheckin'] = int(checkinOptions.get('businessCheckin', '1'))
    configList['nUniCheckin'] = int(checkinOptions.get('universalCheckin', '0'))

    configList['nCoachSecurity'] = int(checkinOptions.get('coachSecurity', '2'))
    configList['nBusiSecurity'] = int(checkinOptions.get('businessSecurity', '1'))
    configList['nUniSecurity'] = int(checkinOptions.get('universalSecurity', '0'))
    
    simOptions = parser['simulation']
    
    configList['simLength'] = int(simOptions.get('simLength', '7'))
    configList['commuterCap'] = int(simOptions.get('commuterCap', '-1'))
    configList['commuterRate'] = int(simOptions.get('commuterRate', '40'))
    
    logOptions = parser['logging']
    
    configList['logQueue'] = int(logOptions.get('logQueue', '1'))
    configList['logPlane'] = int(logOptions.get('logPlane', '1'))
    configList['logPassenger'] = int(logOptions.get('logPassenger', '1'))
    
    configList['printQueue'] = int(logOptions.get('printQueue', '0'))
    configList['printPlane'] = int(logOptions.get('printPlane', '0'))
    configList['printPassenger'] = int(logOptions.get('printPassenger', '0'))
    print(configList)
    return configList
    """
    flightOptions = parser['flights']
    commuterInterval = flightOptions.get('commuterInterval', '60')
    provincialCoachChance = flightOptions.get('provincialCoachChance', '85')
    """
    
def writeDefaultConfig():
    defaultConfig = configparser.ConfigParser()
    
    defaultConfig['checkin'] = {
        'universalQueuePolicy': '1',
        'coachCheckin': '3',
        'businessCheckin': '1',
        'universalCheckin': '0',
        'coachSecurity': '2',
        'businessSecurity': '1',
        'universalSecurity': '0'
    }

    defaultConfig['simulation'] = {
        'simLength': '7',
        'commuterCap': '-1',
        'commuterRate': '40'
    }

    defaultConfig['logging'] = {
        'logQueue': '1',
        'logPlane': '1',
        'logPassenger': '1',
        'printQueue': '0',
        'printPlane': '0',
        'printPassenger': '0'
    }
    
    with open('config.cfg', 'w') as cfgfile:
        defaultConfig.write(cfgfile)