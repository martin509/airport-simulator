import distributions
import scheduler
import checkin
import passenger
import plane
import csv

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
    scheduler.globalQueue.addEventFromFunc(30, plane.CommuterFlight, 2, [])
    
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
        print("Set number of universal security machines:")
        nUniSec = int(input())
        print("Set number of coach security machines:")
        nCoachSec = int(input())
        print("Set number of business security machines:")
        nBusiSec = int(input())
        
        checkin.setupCheckin([0,1,1], [0, 1, 1], [nUniversal,nCoach,nBusiness], [nUniSec, nCoachSec, nBusiSec])
        
    #print("set maximum number of commuters:")
    passenger.Passenger.MAXPASSENGERCOUNT = -1 #int(input()) TODO
   
        
    
if __name__=="__main__" :
    main()
