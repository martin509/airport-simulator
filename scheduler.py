import scheduler
from collections import deque

DEBUG = 0

class GlobalEvent:
    """
    time: the time the event fires
    func: the function that fires when the event fires
    priority: the priority the event takes in the firing order (lower is higher priority)
    """
    def __init__(self, time, func, priority):
        self.eventTime = time
        self.func = func
        self.priority = priority
        self.args = list()
        
    def addArgs(self, args):
        for arg in args:
            self.args.append(arg)
        
    def __str__(self):
        return f'event scheduled for time {self.eventTime}'
    
    def __lt__(self, other):
        return self.priority < other.priority
    
    def __eq__(self, other):
        return self.priority == other.priority
        

class GlobalEventQueue:
    """
    Defines a global queue for the scheduler. 
    All arrivals, departures, etc in all aspects of the application go here.
    """
    MAXTIME = 32
    def __init__(self):
        self.queue = deque()
        self.time = 0
        
    def popNextEvents(self):
        #if the queue has >0 events in it
        if len(self.queue) > 0:
            #advance to the next event's time
            #build a list of all events that occur at the same time
            #return that list
            eventlist = [self.queue.popleft()]
            if DEBUG:
                print(str(eventlist[0]))
            self.time = eventlist[0].eventTime
            is_sametime = 1
            while is_sametime and len(self.queue) > 0: 
                next_event = self.queue.popleft()
                if(next_event.eventTime == self.time):
                    eventlist.append(next_event)
                else:
                    is_sametime = 0
                    self.queue.appendleft(next_event)
            return eventlist
        else:
            return list()
            
            
    def addEvent(self, event):
        #takes a GlobalEvent as var
        #insert it into the queue at the appropriate place w/ respect to time
        i=0;
        if len(self.queue) > 0:
            if DEBUG:
                print("adding event for queue>0")
                print(str(event))
                print(len(self.queue))
            while i <= len(self.queue):
                if DEBUG:
                    print("made it in, i: ", i)
                if i == len(self.queue):
                    self.queue.append(event)
                    return
                elif event.eventTime <= self.queue[i].eventTime:
                    self.queue.insert(i, event)
                    if DEBUG:
                        print("added, queuelength:", len(self.queue))
                    return             
                i+=1;
        else:
            self.queue.append(event)
            if DEBUG:
                print("added, queuelength:", len(self.queue))
            return
            
    def addEventFromFunc(self, time, func, priority, args):
        #add a new event to the scheduler with a relative time, from a function and arguments
        newTime = self.time + time
        newEvent = GlobalEvent(newTime, func, priority)
        newEvent.addArgs(args)
        self.addEvent(newEvent)
        
    def executeEventQueue(self):
        eventlist = self.popNextEvents()
        while(len(eventlist) > 0 and self.time < GlobalEventQueue.MAXTIME):
            #print(len(eventlist))
            eventlist.sort()
            for event in eventlist:
                event.func(*event.args)
            #print(len(globalQueue.queue))
            eventlist = self.popNextEvents()
        