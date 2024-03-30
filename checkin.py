from collections import deque
import distributions
import scheduler

securityQueue = 0
terminal = list()
checkinQueues = 0
checkinServerList = 0


def sendPassengerToTerminal(passenger):
    terminal.append(passenger)

def sendPassengerToSecurity(passenger):
    print(scheduler.globalQueue.time, ": sent passenger [", passenger, "] to security" )
    sendPassengerToTerminal(passenger)

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
        self.checkinDist1 = distributions.DistExponential(2)
        self.checkinDist2 = distributions.DistExponential(1)
        self.checkinDist3 = distributions.DistExponential(3)
        self.isBusy = 0
        
    def getPassengerProcessTime(self, passenger):
        time = self.checkinDist1.genNumber()
        for n in range(passenger.bagCount):
            time += self.checkinDist2.genNumber()
        time += self.checkinDist3.genNumber()
        return time
        
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
    
def setupCheckin(hasUniversal, hasCoach, hasBusiness, nUniversal, nCoach, nBusiness):

    global securityQueue
    securityQueue = PassengerQueue(0)
    global checkinQueues
    checkinQueues = createCheckinQueues(hasUniversal, hasCoach, hasBusiness)
    global checkinServerList
    checkinServerList = createServers(nUniversal, nCoach, nBusiness)
    





        