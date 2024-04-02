from collections import deque
import distributions
import scheduler
import random

commuterTerminal = deque()
provincialTerminal = list()
checkinQueues = 0
securityQueues = 0
checkinServerList = 0
securityServerList = 0


def sendPassengerToTerminal(passenger):
    print(scheduler.globalQueue.time, ": sent passenger [", passenger, "] to terminal" )
    if passenger.passengerType == "PROVINCIAL":
        if passenger.hasMissedFlight():
            print(scheduler.globalQueue.time, ": ", passenger, "has missed their flight!")
        else:
            provincialTerminal.append(passenger)
    else:
        commuterTerminal.append(passenger)

def sendPassengerToSecurity(passenger):
    print(scheduler.globalQueue.time, ": sent passenger [", passenger, "] to security" )
    passenger.findQueue(securityQueues, securityServerList)

class PassengerQueue(deque):
    # acceptable queueTypes: 0 (universal), 1 (coach), 2 (business)
    def __init__(self, queueType):
        deque.__init__(self)
        self.queueType = queueType
        
    def addToQueue(self, passenger):
        self.append(passenger)
       
        
class Server:
    serverCount = 0
    def __init__(self, passengerType):
        # acceptable passengerTypes: 0, 1, 2
        self.passengerType = passengerType
        self.checkinDist1 = distributions.DistExponential(2)
        self.checkinDist2 = distributions.DistExponential(1)
        self.checkinDist3 = distributions.DistExponential(3)
        self.isBusy = 0
        
        Server.serverCount += 1
        self.serverNumber = Server.serverCount
        
        self.queues = checkinQueues
        
    def __str__(self):
        if self.passengerType == 0:
            return f'universal server #{self.serverNumber}'
        elif self.passengerType == 1:
            return f'coach server #{self.serverNumber}'
        else:
            return f'business server #{self.serverNumber}'
        
    def getPassengerProcessTime(self, passenger):
        time = self.checkinDist1.genNumber()
        for n in range(passenger.bagCount):
            time += self.checkinDist2.genNumber()
        time += self.checkinDist3.genNumber()
        return time
        
    def selectPassenger(self):
        usableQueues = list()
        for queue in self.queues:
            if len(queue) > 0:
                #queue priority: 'universal' queues last
                if queue.queueType == self.passengerType:
                    usableQueues.append(queue)
                elif self.passengerType == 0:
                    usableQueues.append(queue)
                elif queue.queueType == 0:
                    usableQueues.append(queue)
        if len(usableQueues) > 0:
            self.processPassenger(usableQueues[0])
        else:
            self.isBusy = 0
            print(scheduler.globalQueue.time, ":", self, "is idle!")
        """
        for queue in checkinQueues:
            if (queue.queueType == self.passengerType or queue.queueType) and len(queue) > 0:
                self.processPassenger(queue)
                return
        for queue in checkinQueues:
            print("queue of type", queue.queueType, ", length", len(queue))
            if (queue.queueType == 0) and (len(queue) > 0):
                self.processPassenger(queue)
                return
        """
       
    
    def processPassenger(self, queue):
        if self.isBusy == 0:
            self.isBusy = 1
            print(scheduler.globalQueue.time, ":", self, "is no longer idle.")
        passenger = queue.popleft()

        #if passenger has missed their flight send them home TODO double check if this works
        # if(passenger.passengerType == "PROVINCIAL" and passenger.expectedDepartureTime > scheduler.globalQueue.time):
        #     print(scheduler.globalQueue.time, "MISSED FLIGHT : passenger: [", passenger, "] missed flight in checkin line")
        #     return

        checkinTime = self.getPassengerProcessTime(passenger)
        print(scheduler.globalQueue.time, ": checking in passenger: [", passenger, "] checkin time:", checkinTime)
        passenger.checkinTime = checkinTime
        passenger.checkinStartTime = scheduler.globalQueue.time

        scheduler.globalQueue.addEventFromFunc(checkinTime, sendPassengerToSecurity, 1, [passenger])
        scheduler.globalQueue.addEventFromFunc(checkinTime, self.selectPassenger, 1, [])
        return
                
        #grab a passenger from a queue
        #post an event in the scheduler for when the passenger exits the queue
        
class SecurityServer(Server):
    serverCount = 0
    def __init__(self, passengerType):
        Server.__init__(self, passengerType)
        self.checkinDist1 = distributions.DistExponential(3)
        self.checkinDist2 = distributions.DistUniform(0,0)
        self.checkinDist3 = distributions.DistUniform(0,0)
        
        SecurityServer.serverCount += 1
        self.serverNumber = SecurityServer.serverCount
        
        self.queues = securityQueues
        
    def __str__(self):
        if self.passengerType == 0:
            return f'universal security machine #{self.serverNumber}'
        elif self.passengerType == 1:
            return f'coach security machine #{self.serverNumber}'
        else:
            return f'business security machine #{self.serverNumber}'
            
    def processPassenger(self, queue):
        if self.isBusy == 0:
            self.isBusy = 1
            print(scheduler.globalQueue.time, ":", self, "is no longer idle.")
        passenger = queue.popleft()

        #if passenger has missed their flight send them home TODO double check if this works
        # if(passenger.passengerType == "PROVINCIAL" and passenger.expectedDepartureTime > scheduler.globalQueue.time):
        #     print(getReadableTime(scheduler.globalQueue.time), "MISSED FLIGHT : passenger: [", passenger, "] missed flight in security line")
        #     return

        checkinTime = self.getPassengerProcessTime(passenger)
        print(scheduler.globalQueue.time, ": processing passenger: [", passenger, "] security check time:", checkinTime)
        passenger.securityStartTime = scheduler.globalQueue.time
        passenger.securityTime = checkinTime
            
        scheduler.globalQueue.addEventFromFunc(checkinTime, sendPassengerToTerminal, 1, [passenger])
        scheduler.globalQueue.addEventFromFunc(checkinTime, self.selectPassenger, 1, [])
        return

"""
# creates queues for check-in or security
"""
def createQueues(hasUniversal, hasCoach, hasBusiness):
    passengerQueues = list()
    if(hasUniversal):
        passengerQueues.append(PassengerQueue(0))
    if(hasCoach):
        passengerQueues.append(PassengerQueue(1))
    if(hasBusiness):
        passengerQueues.append(PassengerQueue(2))
    return passengerQueues

"""
# creates the check-in queues
"""
def createCheckinServers(nUniversal, nCoach, nBusiness):
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

"""
# creates the security queues
"""
def createSecurityMachines(nUniversal, nCoach, nBusiness):
    serverList = list()
    for x in range(nUniversal):
        s = SecurityServer(0)
        serverList.append(s)
    for x in range(nCoach):
        s = SecurityServer(1)
        serverList.append(s)
    for x in range(nBusiness):
        s = SecurityServer(2)
        serverList.append(s)
    return serverList

"""
# creates and configures the check-in and security queues
"""
def setupCheckin(hasQueues, secQueues, nCheckin, nSecurity):
    

    global securityQueues
    securityQueues = createQueues(secQueues[0], secQueues[1], secQueues[2])
    global checkinQueues
    checkinQueues = createQueues(hasQueues[0], hasQueues[1], hasQueues[2])
    global checkinServerList
    checkinServerList = createCheckinServers(nCheckin[0], nCheckin[1], nCheckin[2])
    global securityServerList
    securityServerList = createSecurityMachines(nSecurity[0], nSecurity[1], nSecurity[2])
    





        