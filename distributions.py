import random
import math

def genU():
    #generate uniform from 0-1
    return (float(random.randrange(10000))/10000)

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
        return (genU() * (self.end-self.start)) + self.start
        
class DistExponential(Distribution):
    def __init__(self, average):
        Distribution.__init__(self)
        self.lambdaVal = 1.0/float(average)
    def genNumber(self):
        return math.log(1 - genU())/(self.lambdaVal * -1)
        
class DistBernoulli(Distribution):
    #geometric distribution, not bernoulli
    def __init__(self, failureChance):
        # chance: float from 0-1
        Distribution.__init__(self)
        self.failureChance = failureChance
    
    def genNumber(self):
        return self.genInt()
        
    #perform trials until a failure occurs
    def genInt(self):
        n = 0
        failed = 1
        while(failed):
            if genU() <= self.failureChance:
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
        
    #perform nTrials trials, and tally up number of successes
    def genInt(self):
        n = 0
        for i in range(self.nTrials):
            if genU() <= self.chance:
                n += 1
        return n
        
class DistNormal(Distribution):
    def __init__(self, mean, variance):
        Distribution.__init__(self)
        self.mean = mean
        self.stdev = math.sqrt(float(variance))
        
    def genNumber(self):
        # implementation of the Box-Muller transform method described in the textbook
        u1 = genU()
        if u1 == 0: #in case we get 0, which would cause a domain error on math.log, regenerate until that doesn't happen
            while u1 == 0:
                u1 = genU()
        u2 = genU()
        z = math.sqrt((-2 * math.log(u1))) * math.cos(2 * math.pi * u2)
        # standard normal random variate w/ mean of 0 and variance of 1
        z = self.mean + (z * self.stdev) # correct for mean and variance
        return z
