from collections import deque
import distributions
import scheduler

securityQueue = 0
checkinQueues = 0
checkinServerList = 0

def sendPassengerToSecurity(passenger):
    print(scheduler.globalQueue.time, ": sent passenger [", passenger, "] to security" )

class PassengerQueue(deque):
    # acceptable queueTypes: 0 (universal), 1 (coach), 2 (business)
    def __init__(self, queueType):
        deque.__init__(self)
        self.queueType = queueType
        
    def addToQueue(self, passenger):
        self.append(passenger)
       
        
class Server:
    def __init__(self, passengerType):
        # acceptable passengerTypes: 0, 1, 2
        self.passengerType = passengerType
        self.checkinDistribution = distributions.DistUniform(0.25,2)
        self.isBusy = 0
        
    def getPassengerProcessTime(self, passenger):
        return self.checkinDistribution.genNumber()
        
    def selectPassenger(self):
        for queue in checkinQueues:
            if queue.queueType == self.passengerType and len(queue) > 0:
                self.processPassenger(queue)
                return
        for queue in checkinQueues:
            if queue.queueType == 0 and len(queue) > 0:
                self.processPassenger(queue)
                return
        self.isBusy = 0
        
    
    def processPassenger(self, queue):
        self.isBusy = 1
        passenger = queue.popleft()
        checkinTime = self.getPassengerProcessTime(passenger)
        print(scheduler.globalQueue.time, ": processing passenger: [", passenger, "] checkin time:", checkinTime)
            
        scheduler.globalQueue.addEventFromFunc(checkinTime, sendPassengerToSecurity, 1, [passenger])
        scheduler.globalQueue.addEventFromFunc(checkinTime, self.selectPassenger, 1, [])
        return
                
        #grab a passenger from a queue
        #post an event in the scheduler for when the passenger exits the queue

def createCheckinQueues(hasUniversal, hasCoach, hasBusiness):
    passengerQueues = list()
    if(hasUniversal):
        passengerQueues.append(PassengerQueue(0))
    if(hasCoach):
        passengerQueues.append(PassengerQueue(1))
    if(hasBusiness):
        passengerQueues.append(PassengerQueue(2))
    return passengerQueues

def createServers(nUniversal, nCoach, nBusiness):
    serverList = list()
    for x in range(nUniversal):
        s = Server(0)

        serverList.append(s)
    for x in range(nCoach):
        s = Server(1)

        serverList.append(s)
    for x in range(nBusiness):
        s = Server(2)

        serverList.append(s)
    return serverList
    
securityQueue = PassengerQueue(0)
checkinQueues = createCheckinQueues(1,0,0)
checkinServerList = createServers(2,0,0)
    





        