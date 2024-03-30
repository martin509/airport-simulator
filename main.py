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
    # checkinQueues = checkin.createCheckinQueues(1,0,0)
    
    print("set maximum runtime:")
    scheduler.GlobalEventQueue.MAXTIME = int(input())
    print("set maximum number of commuters:")
    passenger.Passenger.MAXPASSENGERCOUNT = int(input())
    
    print("set number of universal servers:")
    nServers = int(input())
    
    checkin.setupCheckin(1,0,0, nServers,0,0)
    
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
    plane.ProvincialFlight()
    scheduler.globalQueue.addEventFromFunc(30, plane.CommuterFlight, 2, [])
    
    passenger.generateCommuter()
    
    scheduler.globalQueue.executeEventQueue()
   
        
    
if __name__=="__main__" :
    main()