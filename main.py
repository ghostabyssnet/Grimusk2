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
#
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
#
# [x] rewrite init_data and others


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

# TODO: remake
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
            text = hex(pc.cmu.blocks[start + (x-2)].tag)
            win[WIN_MEMORY_DATA].addstr(x, 1, text)
            win[WIN_MEMORY_DATA].refresh()

# ---------
# functions
# ---------

def handle_key(key, pc, stdscr, win):
    # TODO: add checker for which screen we're in
    if (key == curses.KEY_NPAGE):
        pc.screen.con_dex(+1)
    elif (key == curses.KEY_PPAGE):
        pc.screen.con_dex(-1)
    
def main_loop(stdscr, pc):
    # init our screen windows
    win_menu = init_windows(stdscr)
    win_cache = [] # TODO
    win_table = [] # TODO
    windows = win_menu # set menu as base window
    key = ''
    # testing
    if (test.ON == True): 
        t = test.cases_t()
        # run all test cases
        for x in range(0, len(t.cases)):
            t.cases[x].run(pc, windows[WIN_CONSOLE])
    while (pc.QUIT_FLAG == False):
        
        # TODO: complete this bullshit
        if (1 == 1 and windows != win_menu):
            windows = win_menu
        # TODO: you get the idea
        elif (1 == 2 and windows != win_cache):
            windows = win_cache
        
        # handle input
        key = stdscr.getch()
        handle_key(key, pc, stdscr, windows)
        
        # update screen
        update_screen(pc, stdscr, windows)
        
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
