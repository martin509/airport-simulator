import scheduler
import passenger
import distributions
import checkin

class Flight:
    def __init__(self, delay):
        self.flightDelay = delay
        self.departureTime = scheduler.globalQueue.time + delay
        scheduler.globalQueue.addEventFromFunc(delay, self.takeOff, 2, list())
        
    def takeOff(self):
        print(scheduler.globalQueue.time, ": flight", self, "taking off")
        
class CommuterFlight(Flight):
    flightCount = 0
    flightInterval = 60
    
    def __init__(self):
        Flight.__init__(self, CommuterFlight.flightInterval)
        
        self.totalSeats = 40
        
        CommuterFlight.flightCount += 1
        self.flightNumber = CommuterFlight.flightCount
        
    def __str__(self):
        return f'Commuter flight #{self.flightNumber} scheduled for {self.departureTime}'
        
    def takeOff(self):
        passengers = list()
        print("commuter terminal length:",  len(checkin.commuterTerminal))
        while len(passengers) < self.totalSeats and len(checkin.commuterTerminal) > 0:
            passenger = checkin.commuterTerminal.popleft()
            passengers.append(passenger)
        print(scheduler.globalQueue.time, ":", self, "taking off with", len(passengers), "passengers")
        CommuterFlight()
        
        
class ProvincialFlight(Flight):
    flightCount = 0
    flightInterval = 360
    
    def __init__(self):
        Flight.__init__(self, ProvincialFlight.flightInterval)
        self.coachSeats = 140
        self.businessSeats = 40
        # self.flightDelay = 360
        
        ProvincialFlight.flightCount += 1
        self.flightNumber = ProvincialFlight.flightCount
        
        self.generatePassengers()

    def __str__(self):
        return f'Provincial flight #{self.flightNumber} scheduled for {self.departureTime}'
        
    def generatePassengers(self):
        self.nCoach = distributions.DistBinomial(self.coachSeats, 0.85).genInt()
        self.nBusiness = distributions.DistBinomial(self.businessSeats, 0.75).genInt()
        arrivalDist = distributions.DistNormal(75,50)
        
        # arrival times: assume that provincial flights are generated 6 hours ahead of time
        for n in range(self.nCoach):
            arrivalTime = self.flightDelay - arrivalDist.genNumber()
            scheduler.globalQueue.addEventFromFunc(arrivalTime, passenger.generateProvincial, 2, [self, 1])
            # scheduler.globalQueue.addEventFromFunc(arrivalTime, generateCommuter, 2, list())
        for n in range(self.nBusiness):
            arrivalTime = self.flightDelay - arrivalDist.genNumber()
            scheduler.globalQueue.addEventFromFunc(arrivalTime, passenger.generateProvincial, 2, [self, 2])
            
    def takeOff(self):
        coachPassengers = list()
        businessPassengers = list()
        
        
        
        for passenger in checkin.provincialTerminal:
            if passenger.passengerType == "PROVINCIAL" and passenger.flight == self:
                if passenger.passengerClass == 1:
                    coachPassengers.append(passenger)
                    checkin.provincialTerminal.remove(passenger)
                else:
                    businessPassengers.append(passenger)
                    checkin.provincialTerminal.remove(passenger)
        print(scheduler.globalQueue.time, ":", self, "taking off with", len(coachPassengers), "/", self.nCoach,"coach passengers and", len(businessPassengers),"/", self.nBusiness, "business passengers")
        profit = 1000*len(businessPassengers) + 500*len(coachPassengers) - 12000
        print("\tprofit:", profit)
        ProvincialFlight()
            
        
