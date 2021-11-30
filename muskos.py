import curses
import computer as c

logo1=' _._     _,-\'""`-._\n'
logo2='(,-.`._,\'(       |\`-/|\'      muskOS\n'
logo3='    `-.-\' \ )-`( , o o)   made for Grimusk\n'
logo4='          `-    \`_`\"\'-\n'

CPU_SPEED = 100 # cpu speed in miliseconds

def boot(stdscr):
    pc = c.computer
    stdscr.addstr('SYSTEM BOOTING...\n')
    stdscr.addstr(logo1)
    stdscr.addstr(logo2)
    stdscr.addstr(logo3)
    stdscr.addstr(logo4)
    pc.status = 'ON'
    stdscr.refresh()
    curses.napms(2000)
    return pc
    
def process(pc, stdscr, win):
    pass
    
