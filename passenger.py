import scheduler
import distributions
import checkin
import settings

commuterGenerator = distributions.DistExponential(1.5)


passengerList = list()

class Passenger:
    MAXPASSENGERCOUNT = -1
    PASSENGERSGENERATED = 0
    BusinessCount = 0
    
    totalCheckinTime = 0
    totalSecurityTime = 0
    
    totalBusinessCheckinTime = 0
    totalBusinessSecurityTime = 0
    
    def __init__(self, passengerType, passengerClass):
        #possible customer types: "COMMUTER", "PROVINCIAL"
        #possible customer classes: 1 (coach), 2 (business)
        self.creationTime = scheduler.globalQueue.time
        self.arrivalTime = -1
        
        self.passengerType = passengerType
        self.passengerClass = passengerClass
        self.expectedDepartureTime = -1

        self.departureTime = -1
        self.checkinTime = -1
        self.securityTime = -1
        self.flightNum = -1;
        
        Passenger.PASSENGERSGENERATED += 1
        self.passengerNumber = Passenger.PASSENGERSGENERATED
        if self.passengerClass == 2:
            Passenger.BusinessCount += 1
        
        self.checkinEnterTime = scheduler.globalQueue.time
        self.checkinLeaveTime = 0
        
        self.securityEnterTime = 0
        self.securityLeaveTime = 0
        
        if(passengerType == "COMMUTER"): 
            self.bagCount = distributions.DistBernoulli(0.6).genNumber()
        else:
            self.bagCount = distributions.DistBernoulli(0.8).genNumber()
    
    def __str__(self):
         return f'Coach commuter passenger #{self.passengerNumber} created at {self.creationTime} with {self.bagCount} bags'
         
    def findQueue(self, queues, servers):
        queue1 = 0
        queue2 = 0
        #first loop to look for queue that fits
        for queue in queues:
            if queue.queueType == self.passengerClass:
                queue1 = queue
        # second loop to look for universal queue
        for queue in queues:
            if queue.queueType == 0:
                queue2 = queue
                
        if(queue1 != 0 and queue2 != 0):
            if len(queue1) <= len(queue2):
                self.enterQueue(queue1, servers)
                return
            else:
                self.enterQueue(queue2, servers)
                return
        elif queue1 != 0:
            self.enterQueue(queue1, servers)
            return
        elif queue2 != 0:
            self.enterQueue(queue2, servers)
            return
        print("ERROR: CUSTOMER", self, "COULD NOT FIND QUEUE") #if we get here something bad has happened
    
    def enterQueue(self, queue, servers):
        queue.append(self)
        if(settings.logPassengerInfo):
            print(scheduler.globalQueue.time, ": passenger", self, "entered queue of length ", len(queue))
        for server in servers:
            if server.isBusy == 0 and (server.passengerType == self.passengerClass or server.passengerType == 0):
                server.selectPassenger()
                break
    

    def printFull(self):
        a1 = self.passengerNumber                             #passenger id
        a2 = self.passengerType                               #commuter or provincial
        a3 = ("BUSINESS", "COACH") [self.passengerClass == 1] #coach or business
        a4 = self.bagCount                                    #bag count
        a5 = self.flightNum                                        #flight on if commuter or scheduled flight if provincial
        a6 = self.creationTime                                #creation time
        a7 = self.arrivalTime                                 #arrival time
        
        #checkin waiting time
        a8 = -1
        if self.checkinLeaveTime > 0:
            a8 = self.checkinLeaveTime - self.checkinEnterTime    
        else:
            a8 = scheduler.globalQueue.time
        #checkin time
        a9 = self.checkinTime                                 
        
        #security waiting time
        a10 = -1
        if self.securityLeaveTime > 0:
            a10 = self.securityLeaveTime - self.securityEnterTime 
        else:
            a10 = scheduler.globalQueue.time
        a11 = self.securityTime                               #security time
        a12 = self.departureTime                              #departure time
        # a13 = self.expectedDepartureTime
            
        return [a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11, a12]
        
    def printMin(self):
        if(self.passengerType == "PROVINCIAL"):
            flightType = "P"
        else:
            flightType = "C"
        if(self.passengerClass == 1):
            passType = "C"
        else:
            passType = "B"
        
        return f'P#{self.passengerNumber} ({flightType}{passType})'

    def logStats(self):
        Passenger.totalCheckinTime += (self.checkinLeaveTime - self.checkinEnterTime)
        Passenger.totalSecurityTime += (self.securityLeaveTime - self.securityEnterTime)
        if self.passengerClass == 2:
            Passenger.totalBusinessCheckinTime += (self.checkinLeaveTime - self.checkinEnterTime)
            Passenger.totalBusinessSecurityTime += (self.securityLeaveTime - self.securityEnterTime)
        
class ProvincialPassenger(Passenger):
    coachRefundCount = 0
    businessRefundCount = 0
    def __init__(self, flight, passengerClass):
        Passenger.__init__(self, "PROVINCIAL", passengerClass )
        self.flight = flight
        self.departureTime = flight.departureTime
        self.flightNum = self.flight.flightNumber
        
    def __str__(self):
        if self.passengerClass == 1:
            return f'Coach provincial passenger #{self.passengerNumber} created at {self.creationTime} with {self.bagCount} bags, for {self.flight}'
        else:
            return f'Business provincial passenger #{self.passengerNumber} created at {self.creationTime} with {self.bagCount} bags, for {self.flight}'
            
    def findQueue(self, queues, servers):
        #catching provincial passengers that arrive after the flight's left
        if not self.hasMissedFlight():
            Passenger.findQueue(self, queues, servers)
            
    def hasMissedFlight(self):
        if scheduler.globalQueue.time > self.flight.departureTime:
            print(scheduler.globalQueue.time, ": ", self, "has missed their flight!")
            if (self.expectedDepartureTime - (self.creationTime+self.arrivalTime)) >= 90:
                print(scheduler.globalQueue.time, ": ", self, "qualifies for a ticket refund!")
                if self.passengerClass == 1:
                    ProvincialPassenger.coachRefundCount += 1
                else:
                    ProvincialPassenger.businessRefundCount += 1
            return 
        
         
def generateCommuter():
    newPassenger = Passenger("COMMUTER", 1)
    passengerList.append(newPassenger);
    arrivalTime = commuterGenerator.genNumber()
    newPassenger.creationTime = scheduler.globalQueue.time
    newPassenger.arrivalTime = arrivalTime
    if(settings.logPassengerInfo):
        print(scheduler.globalQueue.time, ": Commuter arrived:", newPassenger, "next arrival time:", arrivalTime)
    newPassenger.findQueue(checkin.checkinQueues, checkin.checkinServerList)
    if(Passenger.PASSENGERSGENERATED < Passenger.MAXPASSENGERCOUNT or Passenger.MAXPASSENGERCOUNT == -1):
        scheduler.globalQueue.addEventFromFunc(arrivalTime, generateCommuter, 2, list())
        
def generateProvincial(passengerClass, flight):
    newPassenger = ProvincialPassenger(passengerClass, flight)
    passengerList.append(newPassenger);
    if(settings.logPassengerInfo):
        print(scheduler.globalQueue.time, ": PROVINCIAL arrived:", newPassenger)
    newPassenger.findQueue(checkin.checkinQueues, checkin.checkinServerList)
    
def endSimStats():
    print("Average passenger check-in queue time:", Passenger.totalCheckinTime/Passenger.PASSENGERSGENERATED)
    print("Average passenger security queue time:", Passenger.totalSecurityTime/Passenger.PASSENGERSGENERATED)
    print("")
    print("Average business class check-in queue time:", Passenger.totalBusinessCheckinTime/Passenger.BusinessCount)
    print("Average business class security queue time:", Passenger.totalBusinessSecurityTime/Passenger.BusinessCount)
    print("")
    print("Number of refunds:", ProvincialPassenger.coachRefundCount + ProvincialPassenger.businessRefundCount)
    totalRefund = ProvincialPassenger.coachRefundCount*500 + ProvincialPassenger.businessRefundCount*1000
    print("Total money refunded: $", totalRefund)
    return totalRefund