import curses
import computer as c

# turns testing on
ON = True

# check system boot
class case_0():
    def run(self, pc, win):
        c.debug(pc, 'Testing CPU')
        
        msg = 'cache layers: ' + str(len(pc.cpu.cores))
        c.debug(pc, msg)
        
        z = len(pc.screen.console_msg)
        y = pc.screen.console_index
        msg = 'size: ' + str(z) + ', index: ' + str(y)
        c.debug(pc, msg)
        #pc.screen.console_index += 2

# RAM & cache I/O
class case_1():
    def run(self, pc, win):
        pass

class cases_t():
    count = 0
    cases = []
    def __init__(self):
        c = case_0()
        self.cases.append(c)
        
        #c = case_1()
        #self.cases.append(c)
    
    
    
