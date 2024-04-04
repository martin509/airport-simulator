import os
from datetime import datetime

import scheduler

writeToConsole = 1
writeToFile = 1
logFolder = ""
logTypes = list()
printTypes = list()

def addLogTypes(types):
    if types[0]:
        logTypes.append('queue')
    if types[1]:
        logTypes.append('plane')
    if types[2]:
        logTypes.append('passenger')
        
def addPrintTypes(types):
    if types[0]:
        printTypes.append('queue')
    if types[1]:
        printTypes.append('plane')
    if types[2]:
        printTypes.append('passenger')

def setupFiles():
    global logFolder
    logFolder = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    logFolder = logFolder[1:]
    logFolder = 'logs/' + logFolder
    os.makedirs('logs', exist_ok=True)
    print("log folder:", logFolder)
    print("timestamp:", datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    os.makedirs(logFolder, exist_ok=True)

    

def writeLog(text, logType):
    # log types: 'queue', 'plane', 'passenger'
    if logType in logTypes:
        global logFolder
        with open(os.path.join(logFolder, 'log.txt'), 'a') as file:
            file.write(f'{scheduler.globalQueue.time} : {text}\n')
    if logType in printTypes:
        print(scheduler.globalQueue.time, ":", text)