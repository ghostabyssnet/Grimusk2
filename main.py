import curses
import muskos as musk
import computer as c
import test_cases as test

# TODO:
# [ ] enable printing to console instead of curses as a toggle
# [ ] GASM compiler
# [ ] instruction set remake: now search for tag instead of addr
# https://inst.eecs.berkeley.edu/~cs61c/resources/su18_lec/Lecture14.pdf
# [x] change collect to be less garbage (wtf is that result)
# [ ] count total lines of code
# 
# -----------------------
# data saving and loading
# -----------------------
# [!] save to cache
# [!] save to ram when no free slots
# -- save from ram to disk when no free ram
# -- warn when disk is full and can't be saved
#
# [!] load from cache
# [!] change priority when loading from a higher cache
# [!] load from ram when not on cache
# -- load from disk when not on ram
# [ ] create data when it's nowhere? design?

# -----------------
# curses visualizer
# -----------------

WIN_INPUT = 0
WIN_CONSOLE = 1
WIN_MEMORY_INSTR = 2
WIN_MEMORY_DATA = 3
WIN_CPU = 4
WIN_GRIMUSK = 5

def init_colors():
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK)
    # debug messages
    curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_WHITE)

def init_windows(stdscr):
    result = []
    win_cpu = curses.newwin(3, 56, 0, 0)
    win_memory_instr = curses.newwin(24, 12, 3, 0)
    win_console = curses.newwin(24, 32, 3, 12)
    win_memory_data = curses.newwin(24, 12, 3, 44)
    win_input = curses.newwin(5, 26, 27, 0)
    win_grimusk = curses.newwin(5, 26, 27, 30)
    result.append(win_input)
    result.append(win_console)
    result.append(win_memory_instr)
    result.append(win_memory_data)
    result.append(win_cpu)
    result.append(win_grimusk)
    stdscr.refresh()
    init_colors()
    for x in range (0, len(result)):
        result[x].attron(curses.color_pair(1 + x))
        #result[x].border('*','*','*','*','*','*','*','*')
        result[x].border()
        result[x].refresh()
    return result

def update_screen(pc, stdscr, windows):
    print_ram(pc, stdscr, windows, 0, 0)
    print_ram(pc, stdscr, windows, 1, 0)
    pc.screen.print_console(windows[WIN_CONSOLE])
    pc.screen.print_special(windows[WIN_GRIMUSK])
    stdscr.refresh()

# TODO: delete me
def placeholder_del_me(pc, win):
    #p = c.data_t()
    #w = c.word_t()
    # -----
    #w.data = [0, 0, 0, 0, 0]
    #p.word = w
    #p.tag = 128
    # -----
    #pc.cpu.cache[0].alloc(10, p)
    pc.screen.print_console(win)

# initializes screen    
def init_screen(stdscr):
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    stdscr.refresh()
    stdscr.nodelay(True)

# turn off computer
def turn_off(stdscr, pc):
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()
    
# -------
# screens
# -------

def print_ram(pc, screen, win, _type, start):
    # max size = 22
    win[WIN_MEMORY_INSTR].addstr(1, 1, 'INSTR RAM')
    win[WIN_MEMORY_DATA].addstr(1, 1, 'DATA RAM')
    if (_type == 0): # 0 = instruction
        for x in range (2, 23):
            text = hex(start + (x-2))
            win[WIN_MEMORY_INSTR].addstr(x, 1, text)
            win[WIN_MEMORY_INSTR].refresh()
    else: # else = data
        for x in range (2, 23):
            text = hex(pc.cmu.blocks[start + (x-2)].addr)
            win[WIN_MEMORY_DATA].addstr(x, 1, text)
            win[WIN_MEMORY_DATA].refresh()

# ---------
# functions
# ---------

def handle_key(key, pc, stdscr, win):
    if (key == curses.KEY_NPAGE):
        pc.screen.con_dex(+1)
        #msg = 'DEBUG: PAGEUP [' + str(pc.screen.console_index) + ']'
        #c.debug(pc, msg)
        #z = len(pc.screen.console_msg)
        #y = pc.screen.console_index
        #msg = 'size: ' + str(z) + ', index: ' + str(y)
        #c.debug(pc, msg)
    elif (key == curses.KEY_PPAGE):
        pc.screen.con_dex(-1)
        #msg = 'DEBUG: PAGEDOWN [' + str(pc.screen.console_index) + ']'
        #c.debug(pc, msg)
        #z = len(pc.screen.console_msg)
        #y = pc.screen.console_index
        #msg = 'size: ' + str(z) + ', index: ' + str(y)
        #c.debug(pc, msg)
    
def main_loop(stdscr, pc):
    windows = init_windows(stdscr) # init our screen windows
    key = ''
    # testing
    if (test.ON == True): 
        t = test.cases_t()
    t.cases[0].run(pc, windows[WIN_CONSOLE])
    #c.debug(pc, 'Testing CPU')
    while (pc.QUIT_FLAG == False):
        # update screen
        key = stdscr.getch()
        handle_key(key, pc, stdscr, windows)
        #curses.napms(50)
        update_screen(pc, stdscr, windows)
        #placeholder_del_me(pc, windows[WIN_CONSOLE]) # FIXME
        # process new data
        musk.process(pc, stdscr, windows)
        # wait
        curses.napms(musk.CPU_SPEED) # 500ms
    turn_off(stdscr, pc)
    if (pc.status == 'KERNEL PANIC'):
        print('KERNEL PANIC!\n')
    
def main(stdscr):
    init_screen(stdscr) # inits our visualizer
    pc = musk.boot(stdscr) # turns computer on
    main_loop(stdscr, pc) # keeps it in the main loop till shutdown
curses.wrapper(main)
