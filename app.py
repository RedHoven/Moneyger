from cgitb import text
import curses
from datetime import datetime
import logging

logging.basicConfig(filename='moneyger.log', filemode='w', level=logging.DEBUG)
log = logging.getLogger(__file__)

KEYS = {
    'enter': 10,
    'delete' : 127,
    'movement': {
        # arrow keys
        259: 'up',
        258: 'down',
    },
    'quit': ord('q'),
}

DATE_FORMAT = "%d-%m-%Y"

CATEGORIES = [
    'food', 'restaurants', 'beauty', 'home', 'presents'
]

class App:
    
    def __init__(self) -> None:
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)
        self.string = ""
        self.input_win = curses.newwin(1,20, 1,0)
        self.details_win = curses.newwin(3, 20, 2, 0)
        self.init_colors()
        self.details_win.bkgd(' ', curses.color_pair(5))
        
    def init_colors(self):
        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_CYAN)
        curses.init_pair(6,curses.COLOR_BLACK,curses.COLOR_WHITE) 
        self.gb = curses.color_pair(4)
        self.bw = curses.color_pair(6)
    
    def run(self):
        try:
            self.main()
        except Exception as e:
            log.exception('\nException occured')
        finally:
            self.quit()
            log.info("\nquit\n\n")
            
    def draw(self,key):
        self.input_win.clear()
        if key == KEYS['delete']:
            self.string = update_text(self.string,chr(key),True)
        else:
            self.string = update_text(self.string,chr(key))
            
        self.input_win.addstr(self.string)    
        self.input_win.refresh()
            
    def main(self):
        current_time = datetime.now()
        log.info(f"\nstarting the app: {current_time}\n")
        self.stdscr.addstr('Welcome to Moneyger!')
        self.stdscr.move(1,0)
        while True:
            key = self.stdscr.getch()
            log.info(key)
            if key == KEYS['quit']:
                log.info('break')
                break
            elif key == KEYS['enter']:
                self.add_request()
            else:
                self.draw(key)
            
    def add_request(self):
        curses.curs_set(0)
        sum = float(self.string)
        data = dict()
        date = datetime.now().strftime(DATE_FORMAT)
        category = 'food'
        note = 'Enter note: '
        
        data[0] = category
        data[1] = date 
        data[2] = note
        
        focus = 0
        
        self.details_win.addstr(0,0,category)
        self.details_win.addstr(1,0,date)
        self.details_win.addstr(2,0,note)
        self.details_win.refresh()
        
        while True:
            key = self.stdscr.getch()
            log.info(key)
            if key == KEYS['quit']:
                self.quit()
            if key in KEYS['movement']:
                if KEYS['movement'][key] == 'down':
                    screen = curses.newwin(1,20,focus+1,0)
                    screen.bkgd(' ',self.bw)
                    screen.refresh()
                    self.details_win.refresh()
                    focus += 1
        
    def quit(self):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()
        exit()
    
    
def parse_string(string):
    s = ''
    f = 0
    for c in string:
        if c.isdigit():
            if c != '0' or f == 1:
                f = 1
                s += c
    return s

def update_text(text, string, remove=False):
    if text != '' or parse_string(string) != '':
        new_text = parse_string(text + string)
        if remove:
            new_text = new_text[:-1]

        if len(new_text) < 3:
            zeros = '0' * (4 - len(new_text))
            new_text = zeros + new_text
        text = new_text[:-2] + '.' + new_text[-2:]
    return text

        
        

