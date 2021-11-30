import computer as c
import curses

# grimusk2 basic instructions

# -------------
# memory bridge
# -------------

IDK_WHERE = -1 # default cache allocation id
RAM_ID = c.CACHE_LAYERS # RAM is after all caches

# check if addr is stored somewhere already
#def cmu_has_addr(pc, tag):
#    found = False
#    for x in range(0, c.CACHE_LAYERS):
#        for y in range(0, len(pc.cmu.cache[x].lines)):    
    
# get from cmu (with cache and stuff)
# using fully associative mapping
def cmu_get(pc, addr):
    _tag = c.get_tag(addr) # which tag to check for
    found = False
    result = None
    for x in range(0, c.CACHE_LAYERS):
        for y in range(0, len(pc.cmu.cache[x].lines)):
            # check if valid
            if (pc.cmu.cache[x].lines[y].valid == True):
                # check tag
                if (pc.cmu.cache[x].lines[y].tag == _tag):
                    pc.cmu.cache[x].hit += 1
                    pc.cmu.cache[x].cost += pow(10, (x+1)) # 10 100 1000...
                    result = pc.cmu.cache[x].lines[y].word.data
                    pc.cmu.cache[x].lines[y].on_use(pc.cpu.pc) # fire on_use event
                    found = True
                    if (x != 0): # if it's not the first cache
                        for z in range(0, c.CACHE_LAYERS):
                            if (z < x): # apply miss to lower caches
                                pc.cmu.cache[z].miss += 1
                                # transfer to lower cache
                                cache_transfer(pc.cmu.cache[x], pc.cmu.cache[x-1], addr)
                    break # we found it, break the loop
    # if not found, then it's on RAM
    if (found == False):
        pc.cmu.ram.cost += 10000 # RAM cost
        pc.cmu.ram.hit += 1
        cmu_set(pc, addr, RAM_ID) # send to RAM
        result = pc.cmu.blocks[addr].word.data
    return result

# pretty much the same as above but returns if/where it exists
# instead of its value (Python has no overloading)
def cmu_exists(pc, addr):
    _tag = c.get_tag(addr) # which tag to check for
    result = None # NULL if it doesn't exist
    for x in range(0, c.CACHE_LAYERS):
        for y in range(0, len(pc.cmu.cache[x].lines)):
            # check if valid
            if (pc.cmu.cache[x].lines[y].valid == True):
                # check tag
                if (pc.cmu.cache[x].lines[y].tag == _tag):
                    pc.cmu.cache[x].hit += 1
                    pc.cmu.cache[x].cost += pow(10, (x+1)) # 10 100 1000...
                    result = [x, y] # returns an array containing cacheId : where
                    # sends our processor PC timestamp to cacheline
                    pc.cmu.cache[x].lines[y].on_use(pc.cpu.pc)
                    if (x != 0): # if it's not the first cache
                        for z in range(0, c.CACHE_LAYERS):
                            if (z < x): # apply miss to lower caches
                                pc.cmu.cache[z].miss += 1
                                # transfer to lower cache
                                cache_transfer(pc.cmu.cache[x], pc.cmu.cache[x-1], addr)
                    break # we found it, break the loop
    return result

# set to cmu
# also handles caching
def cmu_set(pc, addr, where):
    # if we don't know where, we should use cmu_push
    if (where == RAM_ID): # x + 1 = RAM
        x = c.CACHE_LAYERS - 1 # last cache
        ram_to_cache(pc.cmu, pc.cmu.cache[x], addr)
    elif (where != RAM_ID and where > c.CACHE_LAYERS):
        # TODO: return error
        pass
    else: # we put it wherever asked
        pass
   
# pushes to memory
# handles removing/adding using LRU (least recently used)
def cmu_push(pc, addr, data):
    _exists = cmu_exists(pc, addr)
    if (_exists != None):
        cache_id = _exists[0]
        line_id = _exists[1]
    else: # if it doesn't exist, we send it to cache 1
        pc.cmu.cache[0].push(addr, data)
        
# ----------
# operations
# ----------

def _sta(pc, instr, screen, win):
	pc.cpu.mar = instr[1] # send target address to MAR 
	ram.data[MAR] = cpu.ac # sent
	if LOG_CONSOLE: print('STA called: value ', cpu.ac, ' saved in addr[', MAR, ']')

def _stabuf(value, addr, ram): # STA_BUFFER, same as _sta, used internally
	MAR = addr
	ram.data[MAR] = value
	if LOG_CONSOLE: print('STA called: value ', value, ' saved in addr[', MAR, ']')
	
# we ommit MAR from now onwards, you get the idea
	
def _lda(pc, instr, screen, win):
	cpu.ac = ram.data[instr[1]] # retrieved
	if LOG_CONSOLE: print('LDA called: value ', cpu.ac, ' loaded from addr[', instr[1], ']')

def _ldabuf(addr, ram): # LDA_BUFFER, ditto
	return ram.data[addr]
	if LOG_CONSOLE: print('LDA called: value ', ram.data[addr], ' loaded from addr[', addr, ']')

def _lda_ac(value, cpu): # LDA_BUFFER but to AC
	cpu.ac = value
	if LOG_CONSOLE: print('LDA called: value ', value, ' stored into AC (', cpu.ac, ')')

# we could also use to_sta and to_lda instead of stabuf and ldabuf, it would be slightly more realistic but
# I think it's a bit overkill. I'm keeping this here just in case, though

#def to_sta(instr, value, addr):
#	instr[2] = addr
#	instr[1] = value
#	return instr

def _sum(pc, instr, screen, win): # SUM between two numbers
	_lda_ac(ram.data[instr[1]], cpu) # sends instr[1] to AC
	_lda_ac((cpu.ac + ram.data[instr[2]]), cpu) # adds instr[2] and stores in AC
	if LOG_CONSOLE: print('SUM called: ', ram.data[instr[1]], '[', instr[1], '] + ', ram.data[instr[2]], '[', instr[2], '] = ', cpu.ac, '.')

def _sumbuf(x, y, addr, ram): # SUM_BUFFER
	if LOG_CONSOLE: print('SUM called: ', x, ' + ', y, ' = ', (x + y), '.')
	_stabuf((x + y), addr, ram)

def _sum_ac(value, value2, cpu): # SUM_BUFFER to AC
	if LOG_CONSOLE: print('SUM called: ', value, ' + ', value2, ' = ', (value + value2), ' (AC)')
	_lda_ac((value + value2), cpu)

def __sum(instr, ram): # SUM as it's done by our professor. deprecated because it's not really keen to pipelining
	# we did try, though. see below for a half-half solution that uses _stabuf to store stuff
	ram_value_a = _ldabuf(instr[1], ram)
	ram_value_b = _ldabuf(instr[2], ram)
	result = ram_value_a + ram_value_b
	_stabuf(result, instr[3], ram) # saves our variable by calling STA instead of doing so by itself
	if LOG_CONSOLE: print('SUM called: ', ram_value_a, '[', instr[1], '] + ', ram_value_b, '[', instr[2], '] = ', result, '[', instr[3], ']')

def _sub(pc, instr, screen, win):
	_lda_ac(ram.data[instr[1]], cpu) # sends instr[1] to AC
	_lda_ac((cpu.ac - ram.data[instr[2]]), cpu) # adds instr[2] and stores in AC
	if LOG_CONSOLE: print('SUB called: ', ram.data[instr[1]], '[', instr[1], '] - ', ram.data[instr[2]], '[', instr[2], '] = ', cpu.ac, '.')

def __sub(instr, ram): # same issue as SUM. deprecated, but usable anyway
	ram_value_a = _ldabuf(instr[1], ram)
	ram_value_b = _ldabuf(instr[2], ram)
	result = ram_value_a - ram_value_b
	_stabuf(result, instr[3], ram) # saves our variable by calling STA instead of doing so by itself
	if LOG_CONSOLE: print('SUB called: ', ram_value_a, '[', instr[1], '] - ', ram_value_b, '[', instr[2], '] = ', result, '[', instr[3], ']')

def _subbuf(x, y, addr, ram): # SUB_BUFFER
	if LOG_CONSOLE: print('SUM called: ', x, ' - ', y, ' = ', (x - y), '[', addr, ']')
	_stabuf((x - y), addr, ram)



#def cache_alloc(cache, addr, word_data):
#    cache.lines[addr].word.data = word_data
#    cache.lines[addr].valid = True
#        
#def cache_update(cache, addr, word_data):
#    cache.lines[addr].word.data = word_data
#    cache.lines[addr].valid = True
#    cache.lines[addr].updated = True
#    
#def cache_evict(cache, addr):
#    if (cache.lines[addr].updated == False):
#        cache.lines[addr].valid = False
#        return -1
#    else:
#        data = cache.lines[addr].word.data
#        cache.lines[addr].valid = False
#        cache.lines[addr].updated = False
#        return data
#
#def cache_add(cache, addr, data):
#    if (cache.lines[addr].valid == False):
#        cache_alloc(cache, addr, data)
#    else:
#        cache_update(cache, addr, data)
#    cache.lines[addr].tag = addr + 1024
#    
#def cache_remove(ram, cache, addr):
#    data = cache_evict(cache, addr, word)
#    b = word_t()
#    b.data = data
#    if (data != -1):
#        ram.blocks[addr].word = b
#
#def cache_transfer(_from, _to, addr):
#    _to.lines[addr] = _from.lines[addr]
#    cache_evict(_from, addr) # no need to save our data
#
# gets free address cache
#def cache_get_free(cache):
#    result = -1 # -1 = none
#    x = 0
#    while (x < len(cache.lines)): # loop all cache lines
#        if (cache.lines[x].valid == False):
#            result = x # returns lines addr
#    return result
#
## boolean to check if cache has free space
#def cache_has_space(cache):
#    if (cache_get_free(cache) != -1):
#        return True
#    else:
#        return False
