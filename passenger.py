import scheduler
import distributions
import checkin

commuterGenerator = distributions.DistExponential(1.5)


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
        print(scheduler.globalQueue.time, ": passenger", self, "entered queue of length ", len(queue))
        for server in servers:
            if server.isBusy == 0 and (server.passengerType == self.passengerClass or server.passengerType == 0):
                server.selectPassenger()
                break
        
class ProvincialPassenger(Passenger):
    def __init__(self, flight, passengerClass):
        Passenger.__init__(self, "PROVINCIAL", passengerClass )
        self.flight = flight
        
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
        return scheduler.globalQueue.time > self.flight.departureTime
        
         
def generateCommuter():
    newPassenger = Passenger("COMMUTER", 1)
    arrivalTime = commuterGenerator.genNumber()
    print(scheduler.globalQueue.time, ": Commuter arrived:", newPassenger, "next arrival time:", arrivalTime)
    newPassenger.findQueue(checkin.checkinQueues, checkin.checkinServerList)
    if(Passenger.PASSENGERSGENERATED < Passenger.MAXPASSENGERCOUNT or Passenger.MAXPASSENGERCOUNT == -1):
        scheduler.globalQueue.addEventFromFunc(arrivalTime, generateCommuter, 2, list())
        
def generateProvincial(passengerClass, flight):
    newPassenger = ProvincialPassenger(passengerClass, flight)
    print(scheduler.globalQueue.time, ": PROVINCIAL arrived:", newPassenger)
    newPassenger.findQueue(checkin.checkinQueues, checkin.checkinServerList)
    
    