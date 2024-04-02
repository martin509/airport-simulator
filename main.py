import distributions
import scheduler
import checkin
import passenger
import plane

DEBUG = 0

dist = distributions.DistUniform(0,100)

def genericEvent(event):
    print(event.eventTime, ":", dist.genNumber(), "(priority", event.priority, ")")


def main():
    # sets up simulation congiguration
    getSimulationParametersFromUser()

    # generate provincial flight passengers and departure events for the duration of the simulation
    plane.ProvincialFlight()
    # generate commuter flight passengers for the duration of the simulation
    #passenger.generateCommuter()
    # generate commuter flight departure events for the duration of the simulation
    #scheduler.globalQueue.addEventFromFunc(-30, plane.CommuterFlight, 2, [])
    
    # run through simulation by handling events in the event queue
    scheduler.globalQueue.executeEventQueue()

    #print all passenger data
    for val in passenger.passengerList:
        passengerData = val.printFull()
        print(passengerData)



"""
# gets the configurable options for the simulation from the user
"""
def getSimulationParametersFromUser():
    # get desired simulation runtime in days and convert into minutes
    print("set maximum runtime (days):")
    scheduler.GlobalEventQueue.MAXTIME = int(input()) * 24 * 60

    # configures the check-in desk settings
    print("use default checkin desk options? Y/N:")
    usedefault = "Y"#input() TODO fix
    if usedefault == "Y":
        checkin.setupCheckin([0,1,1], [0, 1, 1], [0,3,1], [0,2,1])
    else:
        print("set number of universal checkin desks:")
        nUniversal = int(input())
        print("set number of coach checkin desks:")
        nCoach = int(input())
        print("set number of business checkin desks:")
        nBusiness = int(input())
        print("set number of universal security machines:")
        nUniSec = int(input())
        print("set number of coach security machines:")
        nCoachSec = int(input())
        print("set number of business security machines:") # TODO remove security customization
        nBusiSec = int(input())
        checkin.setupCheckin([0,1,1], [0, 1, 1], [nUniversal,nCoach,nBusiness], [nUniSec, nCoachSec, nBusiSec])
        
    #print("set maximum number of commuters:")
    passenger.Passenger.MAXPASSENGERCOUNT = -1 #int(input()) TODO
   
        
    
if __name__=="__main__" :
    main()


    
    # example event workings?
    # checkinQueues = checkin.createCheckinQueues(1,0,0)
    """
    event1 = scheduler.GlobalEvent(2, genericEvent, 1) # sequence: ABAB or ABBA
    event1.addArgs([event1])
    event2 = scheduler.GlobalEvent(3, genericEvent, 1)
    event2.addArgs([event2])
    event3 = scheduler.GlobalEvent(3, genericEvent, 2)
    event3.addArgs([event3])
    event4 = scheduler.GlobalEvent(1, genericEvent, 1)
    event4.addArgs([event4])
    
    globalQueue.addEvent(event1)
    globalQueue.addEvent(event2)
    globalQueue.addEvent(event3)
    globalQueue.addEvent(event4)
    """