import os
from datetime import datetime

import scheduler
import csv

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
    logFolder = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    logFolder = logFolder[1:]
    logFolder = 'logs/' + logFolder
    os.makedirs('logs', exist_ok=True)
    print("log folder:", logFolder)
    print("timestamp:", datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    os.makedirs(logFolder, exist_ok=True)
    
    
    
    
    
def setupAllCsv(checkinList, securityList):
    setupCsv('passengers.csv', ["Passenger Number", "Type", "Class", "# of bags", "Flight #", "Arrival time", "Interarrival time", "Checkin queue time", "Checkin processing time", "Security queue time", "Security processing time", "Departure time", "Flight departure time"])
    setupCsv('planes.csv', ["Plane Number", "Type", "Departure Time", "# available coach seats", "# available buasiness seats", "# filled coach seats", "# filled buasiness seats", "# expected coach seats", "# expected buasiness seats", "flight profit"])
    
    for server in checkinList:
        setupCsv(f'checkindesk{server.serverNumber}.csv', [])
    for server in securityList:
        setupCsv(f'securitydesk{server.serverNumber}.csv', [])
    
def setupCsv(name, topRow):
    csv1 = open(os.path.join(logFolder, name), 'w')
    csv1writer = csv.writer(csv1, dialect='excel', lineterminator='\n')
    csv1writer.writerow(topRow)

def writeToCsv(file, row):
    csvWriter = csv.writer(open(os.path.join(logFolder, file), 'a'), dialect='excel', lineterminator='\n')
    csvWriter.writerow(row)
        



def writeLog(text, logType):
    # log types: 'queue', 'plane', 'passenger'
    if logType in logTypes:
        global logFolder
        with open(os.path.join(logFolder, 'log.txt'), 'a') as file:
            file.write(f'{scheduler.globalQueue.time} : {text}\n')
    if logType in printTypes:
        print(scheduler.globalQueue.time, ":", text)