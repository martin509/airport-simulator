import scheduler
import distributions

commuterGenerator = distributions.DistUniform(1,2)


class Passenger:
    MAXPASSENGERCOUNT = -1
    PASSENGERSGENERATED = 0
    
    def __init__(self, creationTime, customerType):
        #possible customer types: "COMMUTER", "PROVINCIAL"
        self.creationTime = creationTime
        self.customerType = customerType
        if(customerType == "COMMUTER"): #TODO: proper statistics
            self.bagCount = int(distributions.DistUniform(0,2).genNumber())
        else:
            self.bagCount = int(distributions.DistUniform(1,3).genNumber())
    
    def __str__(self):
         return f'customer created at {self.creationTime} of type {self.customerType} with {self.bagCount} bags'
        
        
def generateCommuter(scheduler):
    newPassenger = Passenger(scheduler.time, "COMMUTER")
    print("passenger generated:", newPassenger)
    arrivalTime = commuterGenerator.genNumber()
    Passenger.PASSENGERSGENERATED += 1
    if(Passenger.PASSENGERSGENERATED < Passenger.MAXPASSENGERCOUNT or Passenger.MAXPASSENGERCOUNT == -1):
        scheduler.addEventFromFunc(arrivalTime, generateCommuter, 2, [scheduler])
    
    