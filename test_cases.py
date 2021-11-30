import curses
import computer as c
import random

# turns testing on
ON = True

# check system boot
class case_0():
    def run(self, pc, win):
        # ---------
        # cpu check
        # ---------
        
        c.debug(pc, 'Testing CPU')
        
        # check caches
        msg = 'cache layers: ' + str(len(pc.cpu.cores))
        c.debug(pc, msg)
        for x in range(0, c.CACHE_LAYERS):
            msg = 'cache[' + str(x) + '] size: ' + str(len(pc.cpu.cache[x].lines)) + ' (should be ' + str(c.alloc()) + ')'
            c.debug(pc, msg)
        
        # check ram
        msg = 'ram blocks: ' + str(len(pc.cmu.blocks))
        c.debug(pc, msg)

# RAM & cache I/O
class case_1():
    def run(self, pc, win):
        # TODO: cache checking, data storage/retrieval
        
        # check first cache
        for x in range(0, len(pc.cpu.cache[0].lines)):
            data = c.data_t()
            word = c.word_t()
            for y in range(0, 4):
                word.data[y] = random.randint(0, 128)
            data.word = word
            data.tag = x
            pc.cpu.cache[0].push(data)

class cases_t():
    count = 0
    cases = []
    def __init__(self):
        c = case_0()
        self.cases.append(c)
        
        c = case_1()
        self.cases.append(c)
    
    
    
