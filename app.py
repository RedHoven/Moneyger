import curses
from datetime import datetime
import logging
from parsers import update_sum_text,update_text

logging.basicConfig(filename='moneyger.log', filemode='w', level=logging.DEBUG)
log = logging.getLogger(__file__)

KEYS = {
    'minus' : 45,
    'plus' : 61,
    'insert':ord('i'),
    'enter': 10,
    'delete' : 127,
    'up/down':{

        259: 'up',
        258: 'down',
    },
    'right/left': {
        260: 'left',
        261: 'right',    
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
            self.welcome()
        except Exception as e:
            log.exception('\nException occured')
        finally:
            log.info("\nquit\n\n")
            self.quit()
            
    def draw(self,key, processor,string):
        
        if key == KEYS['delete']:
            new_str = processor(string,chr(key),True)
        else:
            new_str = processor(string,chr(key))
        
        return new_str
            
    def welcome(self):
        current_time = datetime.now()
        log.info(f"\nstarting the app: {current_time}\n")
        self.stdscr.addstr('Welcome to Moneyger!')

        string = ''
        sign = '-'
        sum = ''
        
        self.stdscr.move(1,0)
        self.stdscr.addstr('Type to add cost')
        curses.curs_set(1)  
        
        while True:
            key = self.stdscr.getch()
            log.info('Welocome key:'+str(key))
            if key == KEYS['quit']:
                log.info('break')
                break
            elif key == KEYS['enter']:
                self.add_request(string)      
            elif key == KEYS['plus']:
                self.input_win.clear()
                sign = '+'
                string = sign + sum
                self.input_win.addstr(string)
                self.input_win.refresh()
            elif key==  KEYS['minus']:
                self.input_win.clear()
                sign = '-'
                string = sign + sum
                self.input_win.addstr(string)
                self.input_win.refresh()
            else:
                self.input_win.clear()
                sum = self.draw(key, update_sum_text, sum)
                string = sign + sum
                self.input_win.addstr(string)
                self.input_win.refresh()
                
    def handle_sum(self,sum):
        sign = sum[0]
        sum= sum[1:]
        string = sign + sum 
        while True:
            key = self.stdscr.getch()
            log.info(key)
            if key == KEYS['quit']:
                self.quit()
            elif key == KEYS['enter']:
                return string, False
            elif key in KEYS['up/down']:
                if KEYS['up/down'][key] == 'up':
                    self.input_win.bkgd(' ',curses.color_pair(6))
                    self.input_win.refresh()
                elif KEYS['up/down'][key] == 'down':
                    self.input_win.bkgd(' ',curses.color_pair(3))
                    return string, True
            elif key == KEYS['plus']:
                self.input_win.clear()
                sign = '+'
                string = sign + sum
                self.input_win.addstr(string)
                self.input_win.refresh()
            elif key == KEYS['minus']:
                self.input_win.clear()
                sign = '-'
                string = sign + sum
                self.input_win.addstr(string)
                self.input_win.refresh() 
            else:
                self.input_win.clear()
                sum = self.draw(key,update_sum_text,sum)
                string = sign + sum
                self.input_win.addstr(string)
                self.input_win.refresh()
            
            
    def add_request(self,string):
        self.details_win.bkgd(' ',curses.color_pair(3))
        curses.curs_set(0)
        sign = string[0]
        sum = float(string[1:])
        data = dict()
        date = datetime.now().strftime(DATE_FORMAT)
        
        # set the most probable category
        category = 'food'
        note = 'Enter note'
        
        data[0] = string
        data[1] = category
        data[2] = date 
        data[3] = note
        
        self.details_win.addstr(0,0,category)
        self.details_win.addstr(1,0,date)
        self.details_win.addstr(2,0,note)
        self.details_win.refresh()
        
        focus = 0
        focus_pad = curses.newpad(100,100)
        focus_pad.bkgd(' ',self.bw)
        focus_pad.addstr(0,0,category)
        focus_pad.addstr(1,0,date)
        focus_pad.addstr(2,0,note)
        focus_pad.refresh(focus,0,2+focus,0,2+focus,19)
        
        unfocused_pad = curses.newpad(100,100)
        unfocused_pad.bkgd(' ',curses.color_pair(3))
        unfocused_pad.addstr(0,0,category)
        unfocused_pad.addstr(1,0,date)
        unfocused_pad.addstr(2,0,note)

        self.stdscr.move(2,0)
        while True:
            key = self.stdscr.getch()
            log.info(key)
            if key == KEYS['quit']:
                self.quit()
            if key in KEYS['up/down']:
                if KEYS['up/down'][key] == 'down':
                    if focus == -1:
                        focus += 1
                        focus_pad.refresh(focus,0,2+focus,0,2+focus,19)
                    elif focus < len(data)-2:
                        focus += 1
                        unfocused_pad.refresh(focus-1,0,1+focus,0,1+focus,19)    
                        focus_pad.refresh(focus,0,2+focus,0,2+focus,19)
                        
                if KEYS['up/down'][key] == 'up':
                    if focus == -1:
                        unfocused_pad.refresh(focus+1,0,3+focus,0,3+focus,19)
                    elif focus > 0:
                        focus -= 1
                        unfocused_pad.refresh(focus+1,0,3+focus,0,3+focus,19)
                        focus_pad.refresh(focus,0,2+focus,0,2+focus,19)
                    elif focus == 0:
                        unfocused_pad.refresh(focus,0,2+focus,0,2+focus,19)
                        self.input_win.bkgd(' ',curses.color_pair(6))
                        self.input_win.refresh()
                        string, down = self.handle_sum(string)
                        if down:
                            focus_pad.refresh(focus,0,2+focus,0,2+focus,19)
                        else:
                            focus == -1
                        
            else:
                if focus == 0:
                    # category field
                    category = self.сategory_handler(category, key)
                    
                    data[1] = category
                    if category not in CATEGORIES:
                        CATEGORIES.append(category)  
                        
                    log.info(CATEGORIES)  
                    focus_pad.move(0,0)
                    focus_pad.clrtoeol()
                    focus_pad.addstr(0,0,category)
                    unfocused_pad.move(0,0)
                    unfocused_pad.clrtoeol()
                    unfocused_pad.addstr(0,0,category)
                    focus_pad.refresh(focus,0,2+focus,0,2+focus,19)
                        
                if focus == 1:
                    # date handler
                    pass
                
                if focus == 2:
                    # note handler
                    pass
                        
    def сategory_handler(self,category, key):
        if key in KEYS['right/left']:
            if KEYS['right/left'][key] == 'right':
                for i, c in enumerate(CATEGORIES):
                    if c == category and i != len(CATEGORIES)-1:
                        category = CATEGORIES[i+1]
                        break
                    elif c == category:
                        category = CATEGORIES[0]
                        break       
            elif KEYS['right/left'][key] == 'left':
                for i, c in enumerate(CATEGORIES):
                    if c == category and i != 0:
                        category = CATEGORIES[i-1]
                        break
                    elif c == category:
                        category = CATEGORIES[-1]
                        break
        elif key == KEYS['insert']:
            category = self.create_category()
        elif key == KEYS['delete']:
            if len(CATEGORIES) != 1:
                self.delete_category(category)
            category = CATEGORIES[0]
        
        return category    

    def delete_category(self,category):
        for c in CATEGORIES:
            if c == category:
                CATEGORIES.remove(category)
    
    def create_category(self):
        key = self.stdscr.getch()
        category = ''
        category_win = curses.newwin(1,20,2,0)
        category_win.bkgd(' ',self.bw)
        
        while key != KEYS['enter']:
            if key == KEYS['quit']:
                self.quit()
                
            category = self.draw(key,category_win,update_text,category)
            key = self.stdscr.getch()
            
        return category
         
    
    def quit(self):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()
        exit()

        

