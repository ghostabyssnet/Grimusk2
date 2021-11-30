import random
# ----
# init
# ----

MAX_RAM = 256 # 256 blocks of 4 integers instead
# still 1024 integers in total

MAX_DRIVE = 512 # HDD/SSD size 

CACHE_LAYERS = 3 # how many cache layers we have

ALLOC_SIZE = MAX_RAM / 4 # 1/4 of ram, that's what windows tends to use

CPU_CORES = 2 # how many cores we have

# defines the template for our memory tags
# or gets a tag from an address
def get_tag(addr):
    return addr + 1024 # simple yet effective template
    
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
        for y in range(0, 3):
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
        while (x < _alloc):
            addr += 1
            for y in range(0, 3):
                b.data[y] = "NULL" # initializes location as NULL
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
    
# ram info
class ram_t():
    cost = 0
    hit = 0 # ram hit
    
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
class grimebuf_t()
    word = word_t()
    tag = 0
    addr = 0
    
# cache definition
# as seen in
# https://www.gatevidyalay.com/cache-mapping-cache-mapping-techniques/
class cache_t():
    lines = []
    cost = 0 # custo
    hit = 0 # cacheHit
    miss = 0 # cache miss
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
    def has_tag(self, tag):
        addr = -1
        x = 0
        while (x < len(self.lines)):
            if (self.lines[x].tag == tag):
                addr = x
                break
            x += 1
        return addr
    
    # frees the least recently used space (LRU)
    # returns grimebuf_t
    def collect(self):
        if (self.has_space() == True):
            return -1 # do nothing if we still have space left
        line = -1 # result line_id
        uses = 9999999999 # aux
        x = 0
        while (x < len(self.lines)): # loop lines
            if (self.lines[x].used < uses):
                uses = self.lines[x].used
                line = x
            x += 1
        # transfer the removed data to an object
        data = grimebuf_t()
        linedata = self.evict(line)
        data.addr = line
        data.word = linedata.word
        data.tag = linedata.tag
        return data # evicts garbage line and returns its data
    
    # pushes a line to a free slot
    def push(self, data):
        where = self.has_tag()
        if (where != -1):
            # if we already have this tag stored, we update its data
            self.update(where, data)
        else:
            where = self.get_free()
            if (where != -1):
                # if there's space, we store it there
                self.alloc(where, data)
            else:
                to_ram = self.collect()
                
    # write-back policy: this event is fired
    # on cache miss. 
    def on_miss(self, cost):
        pass
            
# central memory unit    
class cmu_t(): # also known as UCM in portuguese
    instr = [] # instruction memory (array of instr_t payloads)
    blocks = [] # RAM data (array of block_t)
    ram = ram_t() # blocks (ram) info datatype
    # our professor told us we could use blocks for this instead
    # but we're no cowards
    def init_blocks(self):
        self.blocks = init_data(MAX_RAM)
    def init_instr(self):
        self.instr = init_instr(MAX_RAM)
    def __init__(self):
        self.init_blocks()
        self.init_cache()
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
    cache = [] # cache data (array of line_t)
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
        
# our computer
class computer():
    status = 'NULL'
    cpu = cpu_t()
    cmu = cmu_t()
    disk = disk_t()
    # screen = (is defined in our visualizer)
    
# ----------
# global API
# ----------

def cache_transfer(_from, _to, addr):
    _to.lines[addr] = _from.lines[addr]
    _from.evict(_from, addr) # no need to save our data
    
def ram_to_cache(ram, cache, addr):
    cache.add(self, addr, ram.blocks[addr].word.data)
