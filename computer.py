import random
# ----
# init
# ----

# TODO: use this on main.py if muskOS is being used (ifcheck)
MAX_RAM = 256 # 256 blocks of 4 integers instead
# still 1024 integers in total

MAX_DRIVE = 512 # HDD/SSD size 

CACHE_LAYERS = 3 # how many cache layers we have

ALLOC_SIZE = MAX_RAM / 4 # 1/4 of ram, that's what windows tends to use

CPU_CORES = 2 # how many cores we have
    
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
    payload = [0, 0, 0, 0, 0]

# word type
class word_t(): # each word has 4 integers as data
    data = [0, 0, 0, 0]

# memory block
class block_t():
    word = word_t()
    updated = False # se ta atualizado

# ram info
class info_t():
    cost = 0 # custo
    hit = 0 # ram hit
    
# cache line
# we used cornell university's lecture as material
# https://www.cs.cornell.edu/courses/cs3410/2013sp/lecture/18-caches3-w.pdf
class line_t():
    word = word_t()
    valid = False # valid flag: set to true when allocated
    updated = False # updated flag: set to true when... updating (writing)
    tag = 0 # flag for fully associative mapping
# cache definition
# as seen in
# https://www.gatevidyalay.com/cache-mapping-cache-mapping-techniques/
class cache_t():
    lines = []
    cost = 0 # custo
    hit = 0 # cacheHit
    miss = 0 # cache miss
            
# central memory unit    
class cmu_t(): # also known as UCM in portuguese
    instr = [] # instruction memory (array of instr_t payloads)
    blocks = [] # RAM data (array of block_t)
    cache = [] # cache data (array of line_t)
    info = info_t() # block info
    # our professor told us we could use blocks for this instead
    # but we're no cowards
    def init_blocks(self):
        self.blocks = init_data(MAX_RAM)
    def init_cache(self):
        self.cache = init_cache(ALLOC_SIZE)
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
    cores = []
    def init_cores(self):
        z = []
        for x in range(0, CPU_CORES):
            c = core_t()
            z.append(c)
        return z
    def __init__(self):
        self.cores = self.init_cores()
    
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
