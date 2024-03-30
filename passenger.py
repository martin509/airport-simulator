import scheduler
import distributions
import checkin

commuterGenerator = distributions.DistExponential(2/3)


class Passenger:
    MAXPASSENGERCOUNT = -1
    PASSENGERSGENERATED = 0
    
    def __init__(self, passengerType, passengerClass):
        #possible customer types: "COMMUTER", "PROVINCIAL"
        #possible customer classes: 1 (coach), 2 (business)
        self.creationTime = scheduler.globalQueue.time
        self.passengerType = passengerType
        self.passengerClass = passengerClass
        
        Passenger.PASSENGERSGENERATED += 1
        self.passengerNumber = Passenger.PASSENGERSGENERATED
        
        if(passengerType == "COMMUTER"): 
            self.bagCount = distributions.DistBernoulli(0.6).genNumber()
        else:
            self.bagCount = distributions.DistBernoulli(0.8).genNumber()
    
    def __str__(self):
         return f'passenger #{self.passengerNumber} of type {self.passengerType} created at {self.creationTime} with {self.bagCount} bags'
         
    def findQueue(self):
        queue1 = 0
        queue2 = 0
        #first loop to look for queue that fits
        for queue in checkin.checkinQueues:
            if queue.queueType == self.passengerType:
                queue1 = queue
        # second loop to look for universal queue
        for queue in checkin.checkinQueues:
            if queue.queueType == 0:
                queue2 = queue
                
        if(queue1 != 0 and queue2 != 0):
            if len(queue1) <= len(queue2):
                queue1.append(self)
                return
            else:
                self.enterQueue(queue2)
                return
        elif queue1 != 0:
            self.enterQueue(queue1)
            return
        elif queue2 != 0:
            self.enterQueue(queue2)
            return
        print("ERROR: CUSTOMER", self, "COULD NOT FIND QUEUE") #if we get here something bad has happened
    
    def enterQueue(self, queue):
        queue.append(self)
        print(scheduler.globalQueue.time, ": passenger", self, "entered queue")
        for server in checkin.checkinServerList:
            # print("checking server: type", server.passengerType,", isBusy:", server.isBusy)
            if server.isBusy == 0 and (server.passengerType == self.passengerClass or server.passengerType == 0):
                server.selectPassenger()
                break
        
class ProvincialPassenger(Passenger):
    def __init__(self, flight, passengerClass):
        Passenger.__init__(self, "PROVINCIAL", passengerClass )
        self.flight = flight
        
    def __str__(self):
        if self.passengerClass == 1:
            return f'Coach passenger #{self.passengerNumber} created at {self.creationTime} with {self.bagCount} bags, for {self.flight}'
        else:
            return f'Business passenger #{self.passengerNumber} created at {self.creationTime} with {self.bagCount} bags, for {self.flight}'
            
    def findQueue(self):
        #catching provincial passengers that arrive after the flight's left
        if scheduler.globalQueue.time <= self.flight.scheduledTime:
            Passenger.findQueue(self)
        
            
         
def generateCommuter():
    newPassenger = Passenger("COMMUTER", 1)
    print(scheduler.globalQueue.time, ": Commuter arrived:", newPassenger)
    arrivalTime = commuterGenerator.genNumber()
    newPassenger.findQueue()
    if(Passenger.PASSENGERSGENERATED < Passenger.MAXPASSENGERCOUNT or Passenger.MAXPASSENGERCOUNT == -1):
        scheduler.globalQueue.addEventFromFunc(arrivalTime, generateCommuter, 2, list())
        
def generateProvincial(passengerClass, flight):
    newPassenger = ProvincialPassenger(passengerClass, flight)
    print(scheduler.globalQueue.time, ": Provincial arrived:", newPassenger)
    newPassenger.findQueue()
    
    