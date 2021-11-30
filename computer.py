import random
import curses

# ----
# init
# ----

MAX_RAM = 256 # 256 blocks of 4 integers instead
# still 1024 integers in total

MAX_DRIVE = 512 # HDD/SSD size 

CACHE_LAYERS = 3 # how many cache layers we have

ALLOC_SIZE = 135 # in total. 45 lines for each cache if using 3 layers

CPU_CORES = 2 # how many cores we have

# ----------------
# screen variables
# ----------------

# turns debug messages on/off
DEBUG = True

# ----------
# error list
# ----------

RAM_FULL = 'RAM_SIZE_ERROR'
CACHE_ALLOC_ERROR = 'CACHE_ALLOC_ERROR'

# -----
# start
# -----

# debugging
def debug(pc, message):
    if (DEBUG != True): return
    pc.screen.console_log(str(message), 7)
    pc.screen.special_log(str(message))
    
# defines how much memory to allocate for caching purposes
def alloc():
    _alloc = int((ALLOC_SIZE / CACHE_LAYERS)) # allocates 1/x of our cache memory
    return _alloc
    
def init_data(size):
    a = []
    b = word_t() # initialize a new word
    c = block_t() # initialize memory block
    x = 0
    aux = -4 # initial address (gets set to 0)
    while (x < MAX_RAM):
        for y in range(0, 4):
            b.data[y] = random.randint(0, 128)
        c.word = b
        aux += 4
        c.addr = aux # set end address to end of word (or 4 int)
        a.append(c) # sends block to array of blocks
        x += 1
    return a # returns array of blocks

def init_cache(size):
    b = word_t() # initialize word
    c = line_t() # initialize cache line
    d = [] # cache_t array (array of array of line_t)
    _alloc = alloc() # how much to alloc
    addr = -1
    aux = -4
    for z in range(0, CACHE_LAYERS):
        x = 0
        a = cache_t() # line_t array
        a.cache_id = z
        while (x < _alloc):
            addr += 1
            for y in range(0, 4):
                b.data[y] = 0 # initializes location as NULL
            c.word = b
            aux += 4
            c.addr = aux
            a.lines.append(c)
            x += 1
        d.append(a)
    return d # returns array of cache lines

def init_instr(size):
    a = []
    b = instr_t()
    b.payload = [0, 0, 0, 0, 0]
    x = 0
    while (x < size):
        a.append(b)
        x += 1
    return a
        
# -------
# classes
# -------

# instruction type
class instr_t():
    # our instruction payload now has 1 more bit
    # for better compatibility with words 
    # (they have 4 bytes of data)
    payload = [0, 0, 0, 0, 0, 0]
    # [OPCODE, IS_WORD, byte1, byte2, byte3, byte4]

# word type
class word_t(): # each word has 4 integers as data
    data = [0, 0, 0, 0]

# memory block
class block_t():
    word = word_t()
    updated = False # check if updated
    tag = 0 # flag for fully associative mapping
    used = 0 # timestamp flag for LRU
    # 0 means unused (useful for malloc() and free())
    # TODO: update the Updated var to false when moving
    # data to cache
    
    # event: this is fired whenever this block is used
    def on_use(self, time):
        # sets used timestamp to now
        self.used = time
    
    # convert its info to grimedata
    def to_data(self):
        data = data_t()
        data.tag = self.tag
        data.word = self.word
        return data
    
# cache line
# we used cornell university's lecture as material
# https://www.cs.cornell.edu/courses/cs3410/2013sp/lecture/18-caches3-w.pdf
class line_t():
    word = word_t()
    valid = False # valid flag: set to true when allocated
    updated = False # updated flag: set to true when... updating (writing)
    tag = 0 # flag for fully associative mapping
    used = 0 # replaces the offset field
    # used as a timestamp flag. shows the last time it was used
    
    # event: this is fired whenever this line is used
    def on_use(self, time):
        # sets used timestamp to now
        self.used = time
        
    # converts its own information to grimedata
    def to_data(self):
        data = data_t()
        data.tag = self.tag
        data.word = self.word
        return data

# grime linedata
# a container for which data we store/get from lines/blocks
class data_t():
    word = word_t()
    tag = 0
    
# grime bufferdata
# a container for data extracted from a cache
class grimebuf_t():
    word = word_t()
    tag = 0
    addr = 0
    
# cache definition
# as seen in
# https://www.gatevidyalay.com/cache-mapping-cache-mapping-techniques/
class cache_t():
    lines = []
    cache_id = 0 # we are at cache[cache_id]
    cost = 0 # custo
    hit = 0 # cacheHit
    miss = 0 # cache miss
    queue = [] # grimebuf queue: send stuff back to ram on update
    # policy: write-back
    
    # -------------------------
    # address related functions
    # -------------------------
    
    def alloc(self, addr, data):
        self.lines[addr].word.data = data.word.data # sets data
        self.lines[addr].valid = True # it's now valid
        self.lines[addr].updated = True
        self.lines[addr].tag = data.tag # sets tag to template
        
    # ditto
    def update(self, addr, data):
        self.lines[addr].word.data = data.word.data
        self.lines[addr].valid = True
        self.lines[addr].updated = True
        self.lines[addr].tag = data.tag # sets tag to template
    
    # returns data_t or -1
    def evict(self, addr):
        if (self.lines[addr].updated == False):
            self.lines[addr].valid = False
            return -1
        else:
            data = self.lines[addr].to_data()
            self.lines[addr].valid = False
            self.lines[addr].updated = False
            return data
        
    # gets free address if cache has it
    def get_free(self):
        result = -1 # -1 = none
        x = 0
        while (x < len(self.lines)): # loop all cache lines
            if (self.lines[x].valid == False):
                result = x # returns lines addr
                break
            x += 1
        self.on_get()
        return result

    # boolean to check if cache has free space
    def has_space(self):
        if (self.get_free() != -1):
            return True
        else:
            return False
    
    # ------------
    # function API
    # ------------
    
    # checks if something with this tag is within our cache lines
    # returns -1 if it doesn't
    def get_tag(self, tag):
        addr = -1
        x = 0
        while (x < len(self.lines)):
            # checks tag and if we have a valid line
            if (self.lines[x].tag == tag and self.lines[x].valid == True):
                addr = x
                break
            x += 1
        self.on_get()
        return addr
    
    # gets the least recently used line
    def get_lru(self):
        line = -1 # result line_id
        uses = 9999999999 # aux
        x = 0
        while (x < len(self.lines)): # loop lines
            if (self.lines[x].used < uses):
                uses = self.lines[x].used
                line = x
            x += 1
        self.on_get()
        return line
    
    # frees the least recently used space (LRU)
    # returns grimebuf_t
    def collect(self):
        if (self.has_space() == True):
            return -1 # do nothing if we still have space left
        line = self.get_lru()
        # transfer the removed data to an object
        data = grimebuf_t()
        linedata = self.evict(line)
        if (linedata == -1):
            data.addr = line
            return data
        data.addr = line
        data.word = linedata.word
        data.tag = linedata.tag
        return data # evicts garbage line and returns its data
    
    # pushes a line to a free slot
    def push(self, data):
        where = self.get_tag(data.tag)
        if (where != -1):
            # if we already have this tag stored, we update its data
            self.update(where, data)
        else:
            where = self.get_free()
            if (where != -1):
                # if there's space, we store it there
                self.alloc(where, data)
            else:
                # if there's no space, we evict a line, send it's
                # info to ram, then store our info there
                to_ram = self.collect()
                # if shtf, we return a fatal error
                # but this shouldn't happen ever
                #if (to_ram.addr == -1):
                #    return CACHE_ALLOC_ERROR
                # send evicted data to queue
                if (to_ram.addr != -1):
                    self.to_queue(to_ram)
                # realloc evicted addr with our data
                self.alloc(to_ram.addr, data)
    
    # ---------
    # queue API
    # ---------
    
    # sends grimebuf data to queue
    def to_queue(self, data):
        self.queue.append(data)
        
    # clears our queue
    # WARNING: data saving should be handled by the PC
    # before calling this (pc.cache_queue())
    def clear_queue(self):
        self.queue = []    
    
    # ---------
    # event API
    # ---------
    
    # write-back policy: this event is fired
    # on cache get attempt
    # (this should be fired every time we use a get_[...])
    def on_get(self):
        # 10 100 1000...
        _cost = pow(10, (1 + self.cache_id))
        self.cost += _cost
        
    # on cache hit
    def on_hit(self, addr, time):
        self.hit += 1
        self.lines[addr].on_use(time)
        
    # on cache miss 
    def on_miss(self):
        self.miss += 1
    
    # on cache update
    def on_update(self):
        pass
    
# central memory unit
# we'll convert it to an array of RAM
# eventually, to simulate multiple memory cards
class cmu_t(): # also known as UCM in portuguese
    instr = [] # instruction memory (array of instr_t payloads)
    blocks = [] # RAM data (array of block_t)
    queue = [] # queue for hard drive saving
    cost = 0
    hit = 0
    
    def alloc(self, addr, data):
        self.blocks[addr].word.data = data.word.data # sets data
        self.blocks[addr].updated = True
        self.blocks[addr].tag = data.tag # sets tag to template
        
    # ditto
    def update(self, addr, data):
        self.blocks[addr].word.data = data.word.data
        self.blocks[addr].updated = True
        self.blocks[addr].tag = data.tag # sets tag to template
    
    # returns data_t
    def evict(self, addr):
        data = self.blocks[addr].to_data()
        self.blocks[addr].updated = False
        self.blocks[addr].tag = 0
        self.blocks[addr].used = 0
        return data
    
    def collect(self):
        if (self.has_space() == True):
            return -1 # do nothing if we still have space left
        block = self.get_lru()
        # transfer the removed data to an object
        data = grimebuf_t()
        blockdata = self.evict(block)
        data.addr = block
        data.word = blockdata.word
        data.tag = blockdata.tag
        return data # evicts garbage block and returns its data
    
    # unused. ram blows itself up if completely used
    def get_lru(self):
        block = -1 # result line_id
        uses = 9999999999 # aux
        x = 0
        while (x < len(self.blocks)): # loop blocks
            if (self.blocks[x].used < uses):
                uses = self.blocks[x].used
                block = x
            x += 1
        self.on_get()
        return block
    
    # checks if RAM blocks have a certain tag
    def get_tag(self, tag):
        addr = -1
        x = 0
        while (x < len(self.blocks)):
            if (self.blocks[x].tag == tag):
                addr = x
                break
            x += 1
        self.on_get()
        return addr
    
    # checks if RAM has a free block slot
    def get_free(self):
        result = -1
        # loop all blocks
        for x in range(0, len(self.blocks)):
            if (self.blocks[x].tag != 0):
                result = x
                break
        self.on_get()
        return result
                
    # -------------
    # data handling
    # -------------
    
    # saves data into RAM
    # returns 0 for success or fatal error
    def save_to_ram(self, data):
        where = self.get_tag(data.tag)
        if (where != -1):
            # if we already have this tag stored, we update its data
            self.update(where, data)
        else:
            where = self.get_free()
            if (where != -1):
                # if there's space, we store it there
                self.alloc(where, data)
            else:
                # returns an overflow error: RAM is full
                return RAM_FULL
        return 0
    
    def on_get(self):
        self.cost += 10000
    
    # activates on ram hit
    def on_hit(self, addr, time):
        self.hit += 1
        self.blocks[addr].on_use(time)
    
    # ---------------
    # everything else
    # ---------------
    
    def init_blocks(self):
        self.blocks = init_data(MAX_RAM)
    def init_instr(self):
        self.instr = init_instr(MAX_RAM)
    def __init__(self):
        self.init_blocks()
        self.init_instr()
        
# cpu core
class core_t():
    threads = [] # assigned threads (instruction sets)

# cpu
# we want to expand to AX / R0 but it's probably too modern
# it has two cores and an interruption handler (TI) now
class cpu_t():
    pc = 0
    ac = 0
    mq = 0
    mar = 0
    mbr = []
    ih = False # interruption handler
    cores = [] # cpu cores
    cache = [] # cache data (array of (array of line_t))
    def init_cores(self):
        z = []
        for x in range(0, CPU_CORES):
            c = core_t()
            z.append(c)
        return z
    def init_cache(self):
        self.cache = init_cache(ALLOC_SIZE)
    def __init__(self):
        self.cores = self.init_cores()
        self.init_cache()
    
# hard/solid state disk
class disk_t():
    blocks = []
    def init_blocks(self):
        self.blocks = init_data(MAX_DRIVE)
    def __init__(self):
        self.init_blocks()

# screen messages
class msg_t():
    message = 'xxx'
    color = 1

# screen/console/monitor
class screen_t():
    cpu_msg = [] # all cpu messages
    console_msg = [] # all console messages
    instr_index = 0
    data_index = [0, 0] # cache/addr
    cpu_index = 0 # index for showing cpu
    console_index = 0 # index for showing console
    color_length = 7 # how many colors we have
    height = 22 # height of console and ram screens
    special_message = ''
    
    def con_dex(self, value):
        x = self.console_index + value
        if (x < 0): return
        elif (x > len(self.console_msg) - self.height): return
        self.console_index = x
    
    def __init__(self):
        self.console_log('     Welcome to Grimusk 2', 4)
        for x in range(0, 24):
            self.console_log(str(x), 1)
    
    def special_log(self, message):
        self.special_message = message
            
    def console_log(self, message, color = 1):
        if (color == 0 or color > self.color_length): color = 1
        if len(message) >= 60:
            r = msg_t()
            r.message = 'this message was too big'
            r.color = 5
            self.console_msg.append(r)
            return
        if len(message) < 30:
            r = msg_t()
            r.message = message
            r.color = color
            # add to message list
            self.console_msg.append(r)
        else:
            x = msg_t()
            x.message = message[0:30]
            x.color = color
            y = msg_t()
            y.message = message[30:(len(message))]
            y.color = color
            self.console_msg.append(x)
            self.console_msg.append(y)
        self.con_dex(+1)
    
    def get_console(self):
        r = []
        start = self.console_index
        for x in range(start, start + 22):
            r.append(self.console_msg[x])
        return r
    
    def print_console(self, win): # to console
        #win.clear()
        array = self.get_console()
        for y in range(0, len(array)):
            msg = array[y]
            end = msg.message
            _y = y + 1
            win.move(_y, 1)
            win.clrtoeol()
            win.refresh()
            _print(win, _y, end, msg.color)
        win.refresh()

    def print_cpu(self, win, start):
        pass # TODO
    
    def print_special(self, win):
        _print(win, 2, self.special_message, 7)
        win.refresh()
    
def _print(win, y, msg, color):
    if (y > 22): return
    try:
        win.addstr(y, 1, msg, curses.color_pair(color))
    except curses.error:
        pass    
    
# our computer
class computer():
    status = 'NULL'
    QUIT_FLAG = False # if we should quit
    cpu = cpu_t()
    cmu = cmu_t()
    disk = disk_t()
    screen = screen_t()
    
    # --------------
    # error handling
    # --------------
    
    # shtf, quit grimusk
    def kernel_panic(self):
        self.QUIT_FLAG = True
        self.status = 'KERNEL PANIC'
    
    # deals with fatal errors
    def fatal_error(self, error):
        if (error == RAM_FULL):
            self.kernel_panic()
    
    # ------------------------
    # inter-hardware functions
    # ------------------------
    
    # promotes data from a cache layer to a lesser one
    # swaps the LRU from the lesser cache
    def promote(self, tag, layer):
        # ignore first cache
        if (layer == 0): return
        # checks if there's free space in the lower layer
        x = self.cpu.cache[layer-1].get_free()
        if (x != -1):
            # where our tag is
            addr = self.cpu.cache[layer].get_tag(tag)
            # our tag's data using its addr
            data = self.cpu.cache[layer].lines[addr]
            # store our data in this free space
            #self.cpu.cache[layer-1].push(data)
            self.cpu.cache[layer-1].alloc(x, data) # directly
            return
        # else...
        # swap this line with the LRU from the lower cache
        this_addr = self.cpu.cache[layer].get_tag(tag)
        lru_addr = self.cpu.cache[layer-1].get_lru()
        aux = self.cpu.cache[layer].lines[this_addr]
        _this = self.cpu.cache[layer].lines[this_addr]
        _lru = self.cpu.cache[layer-1].lines[lru_addr]
        self.cpu.cache[layer].lines[this_addr] = _lru
        self.cpu.cache[layer-1].lines[lru_addr] = aux
        
    # promotes from ram
    def promote_ram(self, tag):
        size = CACHE_LAYERS - 1
        x = self.cpu.cache[size].get_free()
        addr = self.cmu.get_tag(tag)
        data = self.cmu.blocks[addr]
        # if there's free space
        if (x != -1):
            # stores data to the free slot in the last cache
            self.cpu.cache[size].alloc(x, data)
            # evicts the data's original address
            self.cmu.evict(addr)
        else:
            # push to the last cache and let the function
            # transfer stuff to its queue then the RAM
            self.cpu.cache[size].push(data)
            
            # no free space found, gotta move something
            #lru = self.cpu.cache[size].collect()
            
            
    # gets data from either cache or RAM
    # using its tag as reference
    # we use fully associative mapping and look for
    # a tag instead of an address, as seen in
    # https://inst.eecs.berkeley.edu/~cs61c/resources/su18_lec/Lecture14.pdf
    # TODO: look in parallel using our CPU's cores
    def get_data(self, tag):
        found = -1 # flag. will keep being -1 until we find something
        result = data_t() # our result
        # try getting from caches
        # loop all caches
        for x in range(0, CACHE_LAYERS):
            found = self.cpu.cache[x].get_tag(tag)
            if (found != -1): # if we found it
                self.cpu.cache[x].on_hit(found, self.cpu.pc) # give it a hit
                result = self.cpu.cache[x].lines[found].to_data()
                if (x != 0): # if we're not at the first layer
                    # punish all previous caches
                    for z in range (0, CACHE_LAYERS):
                        if (z < x):
                            self.cpu.cache[z].on_miss()
                    # promote this data to a lower cache
                    self.promote(tag, x)
                break
        # if we still didn't find it
        if (found == -1):
            # punish all caches
            for x in range(0, CACHE_LAYERS):
                self.cpu.cache[x].on_miss()
            # try getting from RAM
            found = self.cmu.get_tag(tag)
            if (found != -1): # if found
                self.cmu.on_hit(found, self_cpu.pc)
                result = self.cmu.blocks[found].to_data()
                # promotes from ram
                self.promote_ram(tag)
            else: # if not found, we throw an error
                return -1
        return result
    
    # stores data into memory, handling caching
    # as well using fully associative mapping
    def store_data(self, data):
        pass # TODO
    
    # retrieves data from HDD
    # using its tag as reference
    def get_drive(self, tag):
        pass # TODO
    
    # stores data into HDD
    def store_drive(self, data):
        pass # TODO
    
    # saves cache queues into RAM
    def save_cache_queue(self):
        # loops all caches
        for x in range(0, CACHE_LAYERS):
            queue = self.cpu.cache[x].queue
            # loops this cache's queue
            for x in range(0, len(queue)):
                this = self.cmu.save_to_ram(queue[x]) # queue[x].data?
                if (this == RAM_FULL):
                    self.fatal_error(RAM_FULL)
                    return
            # clear this cache's queue
            self.cpu.cache[x].clear_queue()

# ----------
# global API
# ----------

# stores a grimebuf to ram
def cache_to_ram(data):
    pass

def cache_transfer(_from, _to, addr):
    _to.lines[addr] = _from.lines[addr]
    _from.evict(_from, addr) # no need to save our data
    
def ram_to_cache(ram, cache, addr):
    cache.add(self, addr, ram.blocks[addr].word.data)
