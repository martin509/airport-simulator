import random

class Distribution:
    def __init__(self, start, end):
        self.start = start
        self.end = end
    def genNumber(self):
        pass
        
    def genInt(self):
        return int(genNumber(self))
        
class DistUniform(Distribution):
    def __init__(self, start, end):
        Distribution.__init__(self, start, end)
    def genNumber(self):
        return ((float(random.randrange(10000))/10000) * (self.end-self.start)) + self.start