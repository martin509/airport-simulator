import random
import math

class Distribution:
    def __init__(self):
        pass
        
    def genNumber(self):
        pass
        
    def genInt(self):
        return int(genNumber(self))
        
class DistUniform(Distribution):
    def __init__(self, start, end):
        Distribution.__init__(self)
        self.start = start
        self.end = end
    def genNumber(self):
        return ((float(random.randrange(10000))/10000) * (self.end-self.start)) + self.start
        
class DistExponential(Distribution):
    def __init__(self, average):
        Distribution.__init__(self)
        self.lambdaVal = 1.0/float(average)
    def genNumber(self):
        return math.log( 1- (float(random.randrange(10000))/10000))/(self.lambdaVal*-1)
        
class DistBernoulli(Distribution):
    #technically this is the geometric distribution
    def __init__(self, failureChance):
        # chance: float from 0-1
        Distribution.__init__(self)
        self.failureChance = failureChance
    
    def genNumber(self):
        return self.genInt()
        
    def genInt(self):
        n = 0
        failed = 1
        while(failed):
            if (float(random.randrange(10000))/10000) <= self.failureChance:
                failed = 0
            else:
                n += 1
        return n
        
class DistBinomial(Distribution):
    def __init__(self, nTrials, chance):
        # nTrials: number of trials
        # chance: float from 0-1
        Distribution.__init__(self)
        self.nTrials = nTrials
        self.chance = chance
        
    def genNumber(self):
        return self.genInt()
        
    def genInt(self):
        n = 0
        for i in range(self.nTrials):
            if (float(random.randrange(10000))/10000) <= self.chance:
                n += 1
        return n
        
class DistNormal(Distribution):
    #has to rely on python's normal distribution function since you can't do a variate neatly
    def __init__(self, mean, variance):
        Distribution.__init__(self)
        self.mean = mean
        self.stdev = math.sqrt(float(variance))
        
    def genNumber(self):
        return random.normalvariate(self.mean, self.stdev)