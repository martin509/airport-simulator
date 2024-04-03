import scheduler
import passenger
import distributions
import checkin
import settings

planeList = list()

class Flight:
    def __init__(self, delay):
        self.flightDelay = delay
        self.departureTime = scheduler.globalQueue.time + delay
        scheduler.globalQueue.addEventFromFunc(delay, self.takeOff, 2, list())
        planeList.append(self)
        self.availableCoachSeats = 0
        self.availableBusinessSeats = 0
        self.filledCoachSeats = 0
        self.filledBusinessSeats = 0
        self.expectedCoachSeats = -1
        self.expectedBusinessSeats = -1
        
    def takeOff(self):
        if(settings.logPlaneInfo):
            print(scheduler.globalQueue.time, ": flight", self, "taking off")
    
    def printFull(self):
        a1 = self.flightNumber                  #plane id
        a2 = self.planeType                     #plane type
        a3 = self.departureTime                 #departure time
        a4 = self.availableCoachSeats           #count of available coach seats
        a5 = self.availableBusinessSeats        #count of available buasiness seats
        a6 = self.filledCoachSeats              #count of filled coach seats
        a7 = self.filledBusinessSeats           #count of filled buasiness seats
        a8 = self.expectedCoachSeats              #count of expected coach seats (provincial flights only)
        a9 = self.expectedBusinessSeats           #count of expected buasiness seats (provincial flights only)
        return [a1, a2, a3, a4, a5, a6, a7, a8, a9]
        
class CommuterFlight(Flight):
    flightCount = 0
    flightInterval = 60
    totalFlightProfit = 0
    planeType = "Commuter"
    seatCount = 40
    
    def __init__(self):
        Flight.__init__(self, CommuterFlight.flightInterval)
        
        self.availableCoachSeats = CommuterFlight.seatCount
        
        CommuterFlight.flightCount += 1
        self.flightNumber = CommuterFlight.flightCount
        
    def __str__(self):
        return f'Commuter flight #{self.flightNumber} scheduled for {self.departureTime}'
        
    def takeOff(self):
        passengers = list()
        # if(settings.logPlaneInfo):
        #     print("commuter terminal length:",  len(checkin.commuterTerminal))
        while self.filledCoachSeats < self.availableCoachSeats and len(checkin.commuterTerminal) > 0:
            passenger = checkin.commuterTerminal.popleft()
            passenger.flightNum = self.flightNumber
            passengers.append(passenger)
            passenger.departureTime = self.departureTime
            self.filledCoachSeats += 1
        # self.filledCoachSeats = len(passengers)
        if(settings.logPlaneInfo):
            print(scheduler.globalQueue.time, ":", self, "taking off with", self.filledCoachSeats, "passengers")
        profit = 200 * self.filledCoachSeats - 1500
        if(settings.logPlaneInfo):
            print("\tprofit:", profit)
        CommuterFlight.totalFlightProfit += profit
        CommuterFlight()
        
        
class ProvincialFlight(Flight):
    flightCount = 0
    flightInterval = 360
    totalFlightProfit = 0
    planeType = "Provincial"
    
    coachSeatCount = 140
    coachChance = 0.85
    
    businessSeatCount = 40
    businessChance = 0.75
    
    arrivalMean = 75
    arrivalVariance = 50
    
    def __init__(self):
        Flight.__init__(self, ProvincialFlight.flightInterval)
        # self.coachSeats = 140
        # self.businessSeats = 40
        # self.flightDelay = 360
        self.availableCoachSeats = ProvincialFlight.coachSeatCount
        self.availableBusinessSeats = ProvincialFlight.businessSeatCount
        
        ProvincialFlight.flightCount += 1
        self.flightNumber = ProvincialFlight.flightCount
        
        self.generatePassengers()

    def __str__(self):
        return f'Provincial flight #{self.flightNumber} scheduled for {self.departureTime}'
        
    def generatePassengers(self):
        self.expectedCoachSeats = distributions.DistBinomial(self.availableCoachSeats, ProvincialFlight.coachChance).genInt()
        self.expectedBusinessSeats = distributions.DistBinomial(self.availableBusinessSeats, ProvincialFlight.businessChance).genInt()
        arrivalDist = distributions.DistNormal(ProvincialFlight.arrivalMean, ProvincialFlight.arrivalVariance)
        
        for n in range(self.expectedCoachSeats):
            arrivalTime = ProvincialFlight.flightInterval - arrivalDist.genNumber()
            scheduler.globalQueue.addEventFromFunc(arrivalTime, passenger.generateProvincial, 2, [self, 1])
            # scheduler.globalQueue.addEventFromFunc(arrivalTime, generateCommuter, 2, list())
        for n in range(self.expectedBusinessSeats):
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

        self.filledCoachSeats = len(coachPassengers)
        self.filledBusinessSeats = len(businessPassengers)

        if(settings.logPlaneInfo):
            print(scheduler.globalQueue.time, ":", self, "taking off with", self.filledCoachSeats, "/", self.expectedCoachSeats,"coach passengers and", self.filledBusinessSeats,"/", self.expectedBusinessSeats, "business passengers")
        profit = 1000*self.filledBusinessSeats + 500*self.filledCoachSeats - 12000
        if(settings.logPlaneInfo):
            print("\tprofit:", profit)
        ProvincialFlight.totalFlightProfit += profit
        ProvincialFlight()

def endSimStats():
    print("Total provincial flight profit:", ProvincialFlight.totalFlightProfit)
    if(ProvincialFlight.flightCount > 0): #prevents devide by 0 error
        print("Total provincial flight profit per flight:", round(float(ProvincialFlight.totalFlightProfit)/ProvincialFlight.flightCount, 2))
    print("Total commuter flight profit:", CommuterFlight.totalFlightProfit)
    if(CommuterFlight.flightCount > 0): #prevents devide by 0 error
        print("Total commuter flight profit per flight:", round(float(CommuterFlight.totalFlightProfit)/CommuterFlight.flightCount, 2))
    return ProvincialFlight.totalFlightProfit + CommuterFlight.totalFlightProfit
        
