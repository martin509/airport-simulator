import distributions
import scheduler
import checkin
import passenger
import plane
import csv
import configloader
import logger

DEBUG = 0

dist = distributions.DistUniform(0,100)

def genericEvent(event):
    print(event.eventTime, ":", dist.genNumber(), "(priority", event.priority, ")")


def main():
    logger.setupFiles()
    
    print("Martin and Marcus' Airport Simulator v1.0")
    print("-----------------------------------------")
    # sets up simulation congiguration
    getSimulationParametersFromUser()
    print("")
    print("Running simulation, please wait...")

    # generate provincial flight passengers and departure events for the duration of the simulation
    plane.ProvincialFlight()
    # generate commuter flight passengers for the duration of the simulation
    passenger.generateCommuter()
    # generate commuter flight departure events for the duration of the simulation
    scheduler.globalQueue.addEventFromFunc(-30, plane.CommuterFlight, 2, []) #I changed this to -30 so the first flight is at 00:30am day 1
    
    # run through simulation by handling events in the event queue
    scheduler.globalQueue.executeEventQueue()
    
    logger.writeLog("", 'endstats')
    refunds = passenger.endSimStats()
    logger.writeLog("", 'endstats')
    flights = plane.endSimStats()
    logger.writeLog("", 'endstats')
    agentPay = checkin.endSimStats()
    logger.writeLog("", 'endstats')
    profit = flights - agentPay - refunds
    logger.writeLog(f'Total profit: ${profit}', 'endstats')
    logger.writeLog(f'Average profit per day: ${profit/(scheduler.globalQueue.time/1440)}', 'endstats')
    logger.writeLog(f'Agent pay percentage of revenue: {agentPay/flights}%%', 'endstats')
    
    print("")
    print("Writing logs, please wait...")
    
    logger.setupAllCsv(checkin.checkinServerList, checkin.securityServerList)
    
    #print all passenger data
    for p in passenger.passengerList:
        passengerData = p.printFull()
        logger.writeToCsv('passengers.csv', passengerData)
    
    #print all plane data
    for pl in plane.planeList:
        planeData = pl.printFull()
        logger.writeToCsv('planes.csv', planeData)
    
    #print all server data
    for i in range(len(checkin.checkinServerList)):
        for serverLog in checkin.checkinServerLogs[i]:
            logger.writeToCsv(f'checkindesk{checkin.checkinServerList[i].serverNumber}.csv', serverLog)
    for i in range(len(checkin.securityServerList)):
        for serverLog in checkin.securityServerLogs[i]:
            logger.writeToCsv(f'securitydesk{checkin.checkinServerList[i].serverNumber}.csv', serverLog)
    print("")
    print(f'Logs done! Check folder: logs/{logger.logFolder}!')

"""
# gets the configurable options for the simulation from the user
"""
def getSimulationParametersFromUser():

    print("Load config from file? Y/N (default Y):")
    useconfig = (input().strip() or "Y").upper()
    
    configList = dict()
    if useconfig == "Y":
        print("Enter config filename (default \'config.cfg\')")
        filename = (input().strip() or "config.cfg")
        configList = configloader.loadConfigFile(filename)
            
    else:
        configList = configloader.loadConfigFile('config.cfg')
        # get desired simulation runtime in days and convert into minutes
        print("Set maximum runtime in days (default 7 days):")
        configList['simLength'] = float(input().strip() or "7")

        # configures the check-in desk settings
        print("Use default checkin desk options? Y/N:")
        usedefault = (input().strip() or "Y")
        if usedefault == "Y":
            configList['nUniCheckin'] = 0
            configList['nCoachCheckin'] = 3
            configList['nBusiCheckin'] = 1
        else:
            print("Set number of universal checkin desks:")
            configList['nUniCheckin'] = int(input())
            print("Set number of coach checkin desks:")
            configList['nCoachCheckin'] = int(input())
            print("Set number of business checkin desks:")
            configList['nBusiCheckin'] = int(input())
        
        print("Select universal server policy:")
        print("\t1: Pick from queues randomly, weighted by queue length (pick from longer queues more often)")
        print("\t2: Alternate between queues 50/50")
        print("\t3: Prioritize business-class passengers always")
        print("\t4: Prioritize coach-class passengers always")
        
        configList['universalQueuePolicy'] = int(input().strip() or "1")
        # checkin.Server.universalPolicy = universalPolicy

        # settings.init()
        print("Log all event actions?")
        logthis = input()
        if logthis == "Y":
            configList['logQueue'] = 1
            configList['logPlane'] = 1
            configList['logPassenger'] = 1
        else:
            configList['logQueue'] = 0
            configList['logPlane'] = 0
            configList['logPassenger'] = 0
            
            print("Log queue event actions? Y/N (Default: Y)")
            logthis = (input().strip() or "Y")
            if logthis == "Y":
                configList['logQueue'] = 1
            print("Log plane event actions?")
            logthis = (input().strip() or "Y")
            if logthis == "Y":
                configList['logPlane'] = 1
            print("Log passenger event actions?")
            logthis = (input().strip() or "Y")
            if logthis == "Y":
                configList['logPassenger'] = 1
    

        # print(f'log configuration {settings.logQueueInfo} {settings.logPlaneInfo} {settings.logPassengerInfo}')
        
        
    setSimConfig(configList)
        #print("set maximum number of commuters:")
        # passenger.Passenger.MAXPASSENGERCOUNT = -1 #int(input()) TODO
   
def setSimConfig(configList):

    checkin.Server.universalPolicy = configList['universalQueuePolicy']
    scheduler.GlobalEventQueue.MAXTIME = configList['simLength'] * 1440
    passenger.Passenger.MAXPASSENGERCOUNT = configList['commuterCap']
    
    nUniversal = configList['nUniCheckin']
    nCoach = configList['nCoachCheckin']
    nBusiness = configList['nBusiCheckin']
    
    nUniSec = configList['nUniSecurity']
    nCoachSec = configList['nCoachSecurity']
    nBusiSec = configList['nBusiSecurity']
    
    passenger.setupPassengers(configList['commuterRate'])
    
    plane.CommuterFlight.flightInterval = configList['commuterInterval']
    plane.CommuterFlight.seatCount = configList['commuterSeats']
    
    plane.ProvincialFlight.flightInterval = configList['provincialInterval']
    plane.ProvincialFlight.coachSeatCount = configList['provincialCoachCount'] 
    plane.ProvincialFlight.coachChance = configList['provincialCoachChance']
    plane.ProvincialFlight.businessSeatCount = configList['provincialBusinessCount']
    plane.ProvincialFlight.businessChance = configList['provincialBusinessChance']
    plane.ProvincialFlight.arrivalMean = configList['provincialArrivalMean']
    plane.ProvincialFlight.arrivalVariance = configList['provincialArrivalVariation']
    
    checkin.setupCheckin([0,1,1], [0, 1, 1], [nUniversal,nCoach,nBusiness], [nUniSec,nCoachSec,nBusiSec])
    logger.addLogTypes([bool(configList['logQueue']), bool(configList['logPlane']), bool(configList['logPassenger'])])
    logger.addPrintTypes([bool(configList['printQueue']), bool(configList['printPlane']), bool(configList['printPassenger'])])

if __name__=="__main__" :
    main()
