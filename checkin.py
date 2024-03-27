from collections import deque
import distributions

def createCheckinQueues(nUniversal, nCoach, nBusiness):
    customerQueues = list()
    for x in range(nUniversal):
        customerQueues.append(CustomerQueue(0))
    for x in range(nCoach):
        customerQueues.append(CustomerQueue(1))
    for x in range(nBusiness):
        customerQueues.append(CustomerQueue(2))
    return customerQueues
    
def getCheckinTime(customer):
    return 2
    

class CustomerQueue(deque):
    # acceptable queueTypes: 0 (universal), 1 (coach), 2 (business)
    def __init__(self, queueType):
        deque.__init__(self)
        self.queueType = queueType

class Server:
    def __init__(self, serviceDistribution, customerType):
        self.serviceDistribution = serviceDistribution
        self.customerType = customerType
    
    def process(self, queueList):
        for q in queueList:
            if(q.queueType == self.customerType):
                customer = q.popleft()
                # figure out processing time
                
        #grab a customer from a queue
        #post an event in the scheduler for when the customer exits the queue
        
        
        