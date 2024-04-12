from collections import deque
import distributions
import scheduler
import random
import settings
import copy
import logger

commuterTerminal = deque()
provincialTerminal = deque()

def sendPassengerToTerminal(passenger):
    #if(settings.logPassengerInfo):
    logger.writeLog(f'Passenger entered terminal: {passenger}', 'passenger')
        # print(scheduler.globalQueue.time, ": sent passenger [", passenger, "] to terminal" )
    passenger.logStats()
    if passenger.passengerType == "PROVINCIAL":
        if (passenger.hasMissedFlight()):
            passenger.missFlight()
        else:
            provincialTerminal.append(passenger)
    else:
        commuterTerminal.append(passenger)

def sendPassengerToSecurity(passenger):
    #if(settings.logPassengerInfo):
    logger.writeLog(f'Passenger entered security queue: {passenger}', 'passenger')
    passenger.securityEnterTime = scheduler.globalQueue.time
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
    universalPolicy = 1
    # policy for universal-type servers
    # policy values: 1 (pick randomly), 2 (pick alternating), 3 (prefer business class), 4 (prefer coach class)
    
    def __init__(self, passengerType):
        # acceptable passengerTypes: 0, 1, 2
        self.passengerType = passengerType
        
        self.checkinDist1 = distributions.DistExponential(2)
        self.checkinDist2 = distributions.DistExponential(1)
        self.checkinDist3 = distributions.DistExponential(3)
        
        self.isBusy = 0
        self.totalIdle = 0
        self.totalActive = 0
        self.lastUpdate = 0
        
        Server.serverCount += 1
        self.serverNumber = Server.serverCount
        
        self.queues = checkinQueues
        self.lastQueue = 0
        
    def __str__(self):
        if self.passengerType == 0:
            return f'Universal check-in counter #{self.serverNumber}'
        elif self.passengerType == 1:
            return f'Coach check-in counter #{self.serverNumber}'
        else:
            return f'Business check-in counter #{self.serverNumber}'
        
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
            if Server.universalPolicy == 1:
                self.processPassenger(random.choice(usableQueues))
            elif Server.universalPolicy == 2: # alternate between the two
                for queue in usableQueues:
                    if not (queue == self.lastQueue):
                        self.lastQueue = queue
                        self.processPassenger(queue)
                        return
                self.lastQueue = usableQueues[0]
                self.processPassenger(usableQueues[0])
            elif Server.universalPolicy == 3: # prefer business
                for queue in usableQueues:
                    if queue.queueType == 2:
                        self.processPassenger(queue)
                        return
                self.processPassenger(usableQueues[0])
            elif Server.universalPolicy == 4: # prefer coach
                for queue in usableQueues:
                    if queue.queueType == 1:
                        self.processPassenger(queue)
                        return
                self.processPassenger(usableQueues[0])
                
        else:
            self.updateUtilization()
            self.isBusy = 0
            logger.writeLog(f'{self} is now idle.', 'queue')
            # if(settings.logQueueInfo):
                
                # print(scheduler.globalQueue.time, ":", self, "is idle!")
        
    def updateUtilization(self):
        totalTime = scheduler.globalQueue.time - self.lastUpdate
        if self.isBusy == 0:
            self.totalIdle += totalTime
        else:
            self.totalActive += totalTime
        self.lastUpdate = scheduler.globalQueue.time
        
    def getUtilization(self):
        return float(self.totalActive)/(self.totalIdle + self.totalActive)
    
    def processPassenger(self, queue):
        if self.isBusy == 0:
            self.updateUtilization()
            self.isBusy = 1
            logger.writeLog(f'{self} is no longer idle.', 'queue')
            #if(settings.logQueueInfo):
             #   print(scheduler.globalQueue.time, ":", self, "is no longer idle.")
        passenger = queue.popleft()

        passenger.checkinLeaveTime = scheduler.globalQueue.time
        checkinTime = self.getPassengerProcessTime(passenger)
        logger.writeLog(f'checking in passenger: [{passenger}], process time:{checkinTime}', 'queue')

        passenger.checkinTime = checkinTime
        passenger.checkinStartTime = scheduler.globalQueue.time

        # creates log for this server operation
        # timestamp,Type, # in coach waiting lines, # in business waiting lines, customer being served, time customer spends in checkin
        checkinServerLogs[checkinServerList.index(self)].append([
                scheduler.globalQueue.time,
                ("BUSINESS", "COACH") [passenger.passengerClass == 1],
                # passenger.passengerType,
                len(checkinQueues[0]),
                len(checkinQueues[1]),
                passenger.passengerNumber,
                passenger.checkinTime,
            ])
            
        # if the passenger is going to miss their flight, 
        if passenger.passengerType == "PROVINCIAL": 
            if checkinTime + scheduler.globalQueue.time > passenger.flight.departureTime:
                # post an event for departure time for the passenger leaving the checkin desk and missing their flight
                scheduler.globalQueue.addEventFromFuncAbs(passenger.flight.departureTime, passenger.logStats, 1, [])
                scheduler.globalQueue.addEventFromFuncAbs(passenger.flight.departureTime, passenger.missFlight, 1, [])
                scheduler.globalQueue.addEventFromFuncAbs(passenger.flight.departureTime, self.selectPassenger, 1, [])
                return
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
            return f'Universal security machine #{self.serverNumber}'
        elif self.passengerType == 1:
            return f'Coach security machine #{self.serverNumber}'
        else:
            return f'Business security machine #{self.serverNumber}'
            
    def processPassenger(self, queue):
        if self.isBusy == 0:
            self.updateUtilization()
            self.isBusy = 1
            logger.writeLog(f'{self} is no longer idle.', 'queue')
        passenger = queue.popleft()

        passenger.securityLeaveTime = scheduler.globalQueue.time
        checkinTime = self.getPassengerProcessTime(passenger)
        logger.writeLog(f'processing passenger for security checks: [{passenger}], security check time: {checkinTime}', 'queue')
        passenger.securityStartTime = scheduler.globalQueue.time
        passenger.securityTime = checkinTime

        # creates log for this server operation
        # timestamp,Type, # in coach waiting lines, # in business waiting lines, customer being served, time customer spends in checkin
        securityServerLogs[securityServerList.index(self)].append([
                scheduler.globalQueue.time,
                ("BUSINESS", "COACH") [passenger.passengerClass == 1],
                # passenger.passengerType,
                len(securityQueues[0]),
                len(securityQueues[1]),
                passenger.passengerNumber,
                passenger.checkinTime,
            ])

        if passenger.passengerType == "PROVINCIAL":
            if checkinTime + scheduler.globalQueue.time > passenger.flight.departureTime:

                scheduler.globalQueue.addEventFromFuncAbs(passenger.flight.departureTime, passenger.logStats, 1, [])
                scheduler.globalQueue.addEventFromFuncAbs(passenger.flight.departureTime, passenger.missFlight, 1, [])
                scheduler.globalQueue.addEventFromFuncAbs(passenger.flight.departureTime, self.selectPassenger, 1, [])
                return
            
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

    # this setup works for storing server log information because python lists are guarenteed to stay in same order
    global checkinServerLogs
    checkinServerLogs = list()
    global securityServerLogs
    securityServerLogs = list()
    checkinLogHeaderList = [["timestamp", "Type", "# in coach waiting lines", "# in business waiting lines", "customer being served", "time customer spends in checkin"]]
    securityLogHeaderList = [["timestamp", "Type", "# in coach waiting lines", "# in business waiting lines", "customer being served", "time customer spends in security"]]
    for server in checkinServerList:
        checkinLogHeaderListCopy = copy.deepcopy(checkinLogHeaderList)
        checkinServerLogs.append(checkinLogHeaderListCopy)
    for server in securityServerList:
        securityLogHeaderListCopy = copy.deepcopy(securityLogHeaderList)
        securityServerLogs.append(securityLogHeaderListCopy)
    
def endSimStats():
    global checkinServerList
    global securityServerList
    for server in checkinServerList:
        server.updateUtilization()
        logger.writeLog(f'{server} average utilization: {round(server.getUtilization()*100,2)}%%', 'endstats')
    for server in securityServerList:
        server.updateUtilization()
        logger.writeLog(f'{server} average utilization: {round(server.getUtilization()*100,2)}%%', 'endstats')
    serverPay = len(checkinServerList) * 35 * (float(scheduler.globalQueue.time)/60)
    serverPay = round(serverPay, 2)
    logger.writeLog(f'Total amount paid to checkin agents: ${serverPay}', 'endstats')
    return serverPay
    
    





        