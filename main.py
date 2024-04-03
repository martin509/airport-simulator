import distributions
import scheduler
import checkin
import passenger
import plane
import csv
import settings

DEBUG = 0

dist = distributions.DistUniform(0,100)

def genericEvent(event):
    print(event.eventTime, ":", dist.genNumber(), "(priority", event.priority, ")")


def main():
    print("Martin and Marcus' Airport Simulator v1.0")
    print("-----------------------------------------")
    # sets up simulation congiguration
    getSimulationParametersFromUser()

    # generate provincial flight passengers and departure events for the duration of the simulation
    plane.ProvincialFlight()
    # generate commuter flight passengers for the duration of the simulation
    passenger.generateCommuter()
    # generate commuter flight departure events for the duration of the simulation
    scheduler.globalQueue.addEventFromFunc(-30, plane.CommuterFlight, 2, []) #I changed this to -30 so the first flight is at 00:30am day 1
    
    # run through simulation by handling events in the event queue
    scheduler.globalQueue.executeEventQueue()
    
    passengerFile = open('passengerLogs.csv', 'w')
    passengerWriter = csv.writer(passengerFile, dialect='excel', lineterminator='\n')
    passengerWriter.writerow(["Passenger Number", "Type", "Class", "# of bags", "Flight #", "Arrival time", "Interarrival time", "Checkin queue time", "Checkin processing time", "Security queue time", "Security processing time", "Departure time", "Flight departure time"])
    
    #print all passenger data
    for p in passenger.passengerList:
        passengerData = p.printFull()
        passengerWriter.writerow(passengerData)
        # print(passengerData)

"""
# gets the configurable options for the simulation from the user
"""
def getSimulationParametersFromUser():
    # get desired simulation runtime in days and convert into minutes
    print("Set maximum runtime in days (default 1 day):")
    scheduler.GlobalEventQueue.MAXTIME = float(input().strip() or "1") * 1440

    # configures the check-in desk settings
    print("Use default checkin desk options? Y/N:")
    usedefault = (input().strip() or "Y")
    if usedefault == "Y":
        checkin.setupCheckin([0,1,1], [0, 1, 1], [0,3,1], [0,2,1])
    else:
        print("Set number of universal checkin desks:")
        nUniversal = int(input())
        print("Set number of coach checkin desks:")
        nCoach = int(input())
        print("Set number of business checkin desks:")
        nBusiness = int(input())
        # print("set number of universal security machines:")
        # nUniSec = int(input())
        # print("set number of coach security machines:")
        # nCoachSec = int(input())
        # print("set number of business security machines:") # TODO remove security customization
        # nBusiSec = int(input())
        checkin.setupCheckin([0,1,1], [0, 1, 1], [nUniversal,nCoach,nBusiness], [0,2,1])
        
    print("Select universal server policy:")
    print("\t1: pick from queues randomly")
    print("\t2: alternate between queues")
    print("\t3: prioritize business-class passengers")
    print("\t4: prioritize coach-class passengers")
    
    universalPolicy = int(input().strip() or "1")
    checkin.Server.universalPolicy = universalPolicy

    settings.init()
    print("Log all event actions?")
    logthis = input()
    if logthis == "Y":
        settings.logQueueInfo = True
        settings.logPlaneInfo = True
        settings.logPassengerInfo = True
    else:
        print("Log queue event actions?")
        logthis = input()
        if logthis == "Y":
            settings.logQueueInfo = True
        print("Log plane event actions?")
        logthis = input()
        if logthis == "Y":
            settings.logPlaneInfo = True
        print("Log passenger event actions?")
        logthis = input()
        if logthis == "Y":
            settings.logPassengerInfo = True
    

    print(f'log configuration {settings.logQueueInfo} {settings.logPlaneInfo} {settings.logPassengerInfo}')
        
    #print("set maximum number of commuters:")
    passenger.Passenger.MAXPASSENGERCOUNT = -1 #int(input()) TODO
   
        
    
if __name__=="__main__" :
    main()
