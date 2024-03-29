import scheduler
import distributions
import checkin

commuterGenerator = distributions.DistUniform(0,1)


class Passenger:
    MAXPASSENGERCOUNT = -1
    PASSENGERSGENERATED = 0
    
    def __init__(self, customerType, customerClass):
        #possible customer types: "COMMUTER", "PROVINCIAL"
        #possible customer classes: 1 (coach), 2 (business)
        self.creationTime = scheduler.globalQueue.time
        self.customerType = customerType
        self.customerClass = customerClass
        self.passengerNumber = Passenger.PASSENGERSGENERATED
        Passenger.PASSENGERSGENERATED += 1
        
        if(customerType == "COMMUTER"): #TODO: proper statistics
            self.bagCount = int(distributions.DistUniform(0,2).genNumber())
        else:
            self.bagCount = int(distributions.DistUniform(1,3).genNumber())
    
    def __str__(self):
         return f'passenger #{self.passengerNumber} of type {self.customerType} created at {self.creationTime} with {self.bagCount} bags'
         
    def findQueue(self):
        queue1 = 0
        queue2 = 0
        #first loop to look for queue that fits
        for queue in checkin.checkinQueues:
            if queue.queueType == self.customerType:
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
            if server.isBusy == 0 and (server.passengerType == self.customerClass or server.passengerType == 0):
                server.selectPassenger()
                break
        
        
        
def generateCommuter():
    newPassenger = Passenger("COMMUTER", 1)
    print(scheduler.globalQueue.time, ": passenger generated:", newPassenger)
    arrivalTime = commuterGenerator.genNumber()
    newPassenger.findQueue()
    if(Passenger.PASSENGERSGENERATED < Passenger.MAXPASSENGERCOUNT or Passenger.MAXPASSENGERCOUNT == -1):
        scheduler.globalQueue.addEventFromFunc(arrivalTime, generateCommuter, 2, list())
    
    