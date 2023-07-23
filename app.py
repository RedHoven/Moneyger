from ast import Pass
import curses
from curses.textpad import rectangle
from datetime import date, datetime, timedelta
import logging
import traceback

from numpy import character
from database import Database, Transaction
from parsers import *

logging.basicConfig(filename='moneyger.log', filemode='w', level=logging.DEBUG,
                    format='%(levelname)s: %(message)s',)
log = logging.getLogger(__file__)

KEYS = {
    'minus' : 45,
    'plus' : 61,
    'insert': [ord('i'), 136, 105],
    'enter': 10,
    'delete' : 127,
    'up/down': [259, 258, 65, 66],
    'up': [259,65],
    'down': [258,66],
    'right/left': [260, 261, 68, 67],
    'left': [260, 68],
    'right': [261, 67],
    'quit': ord('q')
}

DATE_FORMAT = "%d-%m-%Y"

class App:
    
    windows = []
    
    def __init__(self) -> None:
        # init curses
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()                 # read input without Enter 
        self.stdscr.keypad(True)        # enable special chars
        
        # Main window dimensions
        num_rows, num_cols = self.read_app_dims()
        
        # App dimensions
        self.main_width = 30
        self.main_height = 20 
        
        # other dimensions
        self.big_note_height = self.main_height - 17
        self.big_note_width  = self.main_width - 2
        
        if self.main_width > num_cols or self.main_height > num_rows:
            log.info('Closing the app because of too small window')
            self.quit()
        
        self.main_window = curses.newwin(self.main_height,
                                         self.main_width,
                                         (num_rows-self.main_height)//2,
                                         (num_cols-self.main_width)//2)
        
        self.main_window.keypad(True)        # enable special chars for main win
    
        # Main Wins
        self.welcome_win = self.main_window.derwin(5,self.main_width, 0, 0)
        self.input_win = self.main_window.derwin(1, self.main_width-2, 2, 1)
        self.category_win = self.main_window.derwin(1, self.main_width-2, 3, 1)
        self.date_win = self.main_window.derwin(1, self.main_width-2, 4, 1)
        self.note_win = self.main_window.derwin(1, self.big_note_width, 5, 1)
        self.big_note_win = self.main_window.derwin(self.big_note_height, self.big_note_width, 5, 1)
        self.details_win = self.main_window.derwin(7, self.main_width, 0, 0)
        
        self.windows = [self.stdscr, self.welcome_win, self.input_win, self.details_win]
        
        # Important coordinates
        
        # upper left corner of the main window
        self.col_s = (num_cols-self.main_width)//2
        self.row_s = (num_rows-self.main_height)//2
        
        # starting position of a details window message line
        self.details_msg_coords = (self.row_s+1, self.col_s+1)
        
        # Other   
        self.init_colors()
        self.db = Database()
        self.CATEGORIES = self.db.get_categories()
        
    def read_app_dims(self):
        num_rows, num_cols = self.stdscr.getmaxyx()
        return num_rows, num_cols   
        
    def init_colors(self):
        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)       # red on black bg
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)    # yellow on black bg
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)     # white on black bg
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)     # green on black bg
        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_CYAN)      # white on cyan bg
        curses.init_pair(6,curses.COLOR_BLACK,curses.COLOR_WHITE)       # black on white bg
        
        self.white_on_black = curses.color_pair(3)
        self.black_on_white = curses.color_pair(6)
    
    def run(self):
        try:
            self.welcome()
        except Exception as e:
            log.exception('\nException occurred')
        finally:
            log.info("\nquit\n\n")
            self.quit()
            
    def print_request_message(self, message):
        r,c = 1,1
        self.details_win.addstr(r,c," "*(self.main_width-3))
        self.details_win.addstr(r,c, message)
        self.details_win.refresh()
        
    def update_linewin(self, linewin, message, n=None, refresh=True):
        linewin.clear()
        linewin.addstr(self.cut_string(message, n=n))
        if refresh:
            linewin.refresh()
            
    def draw(self, key, processor ,string):
        if key == KEYS['delete']:
            new_str = processor(string,chr(key),True)
        else:
            new_str = processor(string,chr(key))
        
        return new_str
    
    def draw_on_win(self,key, win, processor,string):
        if key == KEYS['delete']:
            new_str = processor(string,chr(key),True)
        else:
            new_str = processor(string,chr(key))
        self.update_linewin(win, new_str)
        return new_str
             
    def cut_string(self, string, n=None):
        if n is None:
            n = self.main_width-3
        processed_str = string
        if len(string) > n:
            processed_str = string[:n]
        return processed_str
    
    def welcome(self):
        current_time = datetime.now()
        log.info(f"starting the app: {current_time}\n")

        string = '' # sign + sum together
        sign = '-'
        sum = ''
        
        self.welcome_win.addstr(1,1,'Welcome to Moneyger!')
        self.input_win.addstr('Type in the cost')
        self.input_win.refresh()
        
        self.welcome_win.box()
        self.welcome_win.refresh()
        curses.curs_set(0)
        
        key = self.main_window.getch()
        string, down = self.sum_handler(sum, key)
        self.add_request(string)
            
    def sum_handler(self,sum, key, highlight=False):
        if len(sum) > 2:
            sign = sum[0]
            sum = sum[1:]
        else:
            string = '' # sign + sum together
            sign = '-'
            sum = ''
            
        string = sign + sum 
        previous_str = string
        
        if highlight:
            self.input_win.bkgd(' ',self.black_on_white)
        else:
            self.input_win.bkgd(' ',self.white_on_black)
        
        while True:
            log.info(key)
            
            if key == KEYS['enter'] and not sum=='':
                return string, False
            
            if key == KEYS['quit']:
                self.quit()
            
            if key in KEYS['down'] and not sum=='':
                return string, True
            
            if key == KEYS['plus']:
                sign = '+'
            elif key == KEYS['minus']:
                sign = '-' 
            else:
                sum = self.draw(key,update_sum_text,sum)
                
            string = sign + sum
            if previous_str != string:
                previous_str = string
                self.update_linewin(self.input_win, self.cut_string(string))
            key = self.main_window.getch()
                            
    def clear_wins(self):
        for w in self.windows:
            w.clear()
            
    def refresh_pad(self, pad, focus, type='focused', direction='down', x= None, y= None):
        x = x
        y = y    
    
        if x is None or y is None:
            x = self.col_s
            y = self.row_s
    
        
        if type == 'focused':
            pad.refresh(2+focus, 0,
                        y+2+focus, x+1,
                        y+2+focus, x+self.main_width-2)
            
        if type == 'unfocused':
            if direction == 'down':
                pad.refresh(2+focus-1,0,
                            y+1+focus,x+1,
                            y+1+focus,x+self.main_width-2)  
            else:
                pad.refresh(2+focus+1,0,
                    y+3+focus,x+1,
                    y+3+focus,x+self.main_width-2)  
            
    def print_focus_message(self, focus:int):
        states =   {0:'Edit Sum',
                    1:'Edit Category',
                    2:'Edit Date',
                    3:'Edit Note'}
        self.print_request_message(states[focus])
    
    def add_request(self, string):
    
        # Init blanc details win
        self.clear_wins()
        self.stdscr.bkgd(' ', curses.color_pair(3))
        self.details_win.box()
        self.print_request_message('Add Request')
        
        sign = string[0]
        sum = float(string[1:])
        data = dict()
        date = datetime.now()
        date_str = datetime.now().strftime(DATE_FORMAT)
        
        # set the most probable category
        category = self.db.get_best_category()
        note = 'Enter note...'
        
        data[0] = string
        data[1] = category
        data[2] = date_str 
        data[3] = note
        
        self.details_win.addstr(2,1,string)
        self.details_win.addstr(3,1,category)
        self.details_win.addstr(4,1,date_str)
        self.details_win.addstr(5,1,note)
        self.details_win.refresh()

        x = self.col_s
        y = self.row_s

        focus = 1           # initialize cursor on category
        focus_pad = curses.newpad(7,self.main_width)
        focus_pad.bkgd(' ',self.black_on_white)
        focus_pad.addstr(2,0,string)
        focus_pad.addstr(3,0,category)
        focus_pad.addstr(4,0,date_str)
        focus_pad.addstr(5,0,note)
        self.refresh_pad(focus_pad, focus)
        
        unfocused_pad = curses.newpad(7,self.main_width)
        unfocused_pad.bkgd(' ',curses.color_pair(3))
        unfocused_pad.addstr(2,0,string)
        unfocused_pad.addstr(3,0,category)
        unfocused_pad.addstr(4,0,date_str)
        unfocused_pad.addstr(5,0,note)

        key = self.main_window.getch()
        log.info(key)
        
        while True:
            if key == KEYS['enter']:
                #save transaction
                sign = string[0]
                sum = float(string[1:])
                transaction = Transaction(
                    sign,
                    sum,
                    category,
                    date,
                    note
                )
                transaction.print()
                self.sync_categories()
                # self.db.add_transaction(transaction)

                self.print_request_message('Saved!')
                log.info('SAVED')
                if focus == -1:
                    self.input_win.bkgd(' ',curses.color_pair(6))
                    self.input_win.refresh()
                else:
                    self.refresh_pad(focus_pad, focus)               
            elif key == KEYS['quit']:
                self.quit()   
            elif key in KEYS['up/down']:
                log.info('Up/down')
                
                if key in KEYS['down']:
                    log.info('down')
                    log.debug('focus: '+str(focus))
                    log.debug('category: '+category)
                    
                    if focus < 3:
                        focus += 1
                        self.refresh_pad(unfocused_pad, focus, 'unfocused')
                        self.refresh_pad(focus_pad, focus)
                        self.print_focus_message(focus)
                        
                if key in KEYS['up']:
                    log.info('up')
                    if focus > 0:
                        focus -= 1
                        self.refresh_pad(unfocused_pad, focus, 'unfocused','up')
                        self.refresh_pad(focus_pad, focus)
                        self.print_focus_message(focus)
                      
            else:
                if focus == 0:
                    string, down = self.sum_handler(string, key, True)
                    
                    # update pads
                    focus_pad.move(2,0)
                    focus_pad.clrtoeol()
                    focus_pad.addstr(2,0,string)
                    
                    unfocused_pad.move(2,0)
                    unfocused_pad.clrtoeol()
                    unfocused_pad.addstr(2,0,string)
                    
                    # turn off highlight
                    self.input_win.bkgd(' ',self.white_on_black)
                    self.input_win.refresh()
                    
                    if down:
                        focus +=1
                    self.refresh_pad(focus_pad, focus)
                    
                elif focus == 1:
                    previous_category = category
                    category = self.сategory_handler(category, key, focus_pad)
                    
                    if category not in self.CATEGORIES:
                        self.CATEGORIES.append(category)  
                        
                    log.info(self.CATEGORIES)  
                    
                    if previous_category != category:
                        self.category_win.bkgd(' ',self.white_on_black)
                        self.category_win.refresh()
                        
                        focus_pad.move(3,0)
                        focus_pad.clrtoeol()
                        focus_pad.addstr(3,0,category)
                        
                        unfocused_pad.move(3,0)
                        unfocused_pad.clrtoeol()
                        unfocused_pad.addstr(3,0,category)
                        
                        self.update_linewin(self.category_win, category, refresh=False)
                        self.refresh_pad(focus_pad, focus)
                        
                elif focus == 2:
                    previous_date = date_str
                    date_str = self.date_handler(date_str, key, focus_pad)
                    date = datetime.strptime(date_str, DATE_FORMAT)
 
                    if previous_date != date_str:
                        self.date_win.bkgd(' ',self.white_on_black)
                        self.date_win.refresh()
                        
                        focus_pad.move(4,0)
                        focus_pad.clrtoeol()
                        focus_pad.addstr(4,0,date_str)
                        
                        unfocused_pad.move(4,0)
                        unfocused_pad.clrtoeol()
                        unfocused_pad.addstr(4,0,date_str)
                        self.update_linewin(self.date_win, date_str, refresh=False)
                        self.refresh_pad(focus_pad, focus)
                
                elif focus == 3:
                    note = self.note_handler(key, note)
                    focus_pad.move(5,0)
                    focus_pad.clrtoeol()
                    
                    unfocused_pad.move(5,0)
                    unfocused_pad.clrtoeol()
                    
                    self.note_win.clear()
                    
                    if len(note) > self.big_note_width - 1:
                        self.note_win.addstr(0,0,note[:self.big_note_width-2]+"…")
                        unfocused_pad.addstr(5,0,note[:self.big_note_width-2]+"…")
                        focus_pad.addstr(5,0,note[:self.big_note_width-2]+"…")
                    else:
                        log.info(len(note))
                        self.note_win.addstr(0, 0,note)
                        unfocused_pad.addstr(5,0,note)
                        focus_pad.addstr(5,0,note)
                        
                    # restore the box  
                    self.details_win.box()
                    self.details_win.refresh()
                        
                    self.refresh_pad(unfocused_pad, focus, 'unfocused')
                    self.refresh_pad(focus_pad, focus)
                
            key = self.main_window.getch()
            log.info(key)
       
    def sync_categories(self):
        self.db.update_categories(self.CATEGORIES)           
                        
    def сategory_handler(self,category, key, focus_pad):
        
        if key in KEYS['right']:
            for i, c in enumerate(self.CATEGORIES):
                if c == category and i != len(self.CATEGORIES)-1:
                    return self.CATEGORIES[i+1]
                elif c == category:
                    return self.CATEGORIES[0]    
                
        elif key in KEYS['left']:
            for i, c in enumerate(self.CATEGORIES):
                if c == category and i != 0:
                    return self.CATEGORIES[i-1]
                
                elif c == category:
                    return self.CATEGORIES[-1]
                
        elif key in KEYS['insert']:
            self.print_request_message('Type in new category!')
            new_category = self.create_category(focus_pad)
            self.print_request_message('Add Request')
            if new_category != '':
                category = new_category

        elif key == KEYS['delete']:
            if len(self.CATEGORIES) != 1:
                self.delete_category(category)
            category = self.CATEGORIES[0]
        
        return category    

    def delete_category(self,category):
        if category not in self.CATEGORIES:
            log.info('No such category')
            return
        
        for c in self.CATEGORIES:
            if c == category:
                self.CATEGORIES.remove(category)
    
    def create_category(self, focus_pad):
        key = self.main_window.getch()
        category = ''
        self.category_win.bkgd(' ',self.black_on_white)
        
        while key != KEYS['enter']:           
            category = self.draw_on_win(key,self.category_win,update_text,category)
            key = self.main_window.getch()
        
        return category
    
    def date_handler(self, date_str, key, focus_pad):
        if key in KEYS['right']:
            #next day    
            this_day = datetime.strptime(date_str, DATE_FORMAT)
            this_day += timedelta(days=1)
            date_str = this_day.strftime(DATE_FORMAT)
            date_str = self.draw_on_win(key,self.date_win,update_date,date_str)
            
        elif key in KEYS['left']:
            #prev day
            this_day = datetime.strptime(date_str, DATE_FORMAT)
            this_day -= timedelta(days=1)
            date_str = this_day.strftime(DATE_FORMAT)
            date_str = self.draw_on_win(key,self.date_win,update_date,date_str)
                   
        elif key in KEYS['insert']:
            self.print_request_message('Type in the date!')
            date_str = self.create_date(self.date_win, focus_pad)
            self.print_request_message('Add Request')
            
        return date_str
         
    def create_date(self, date_win, focus_pad):
        key = self.main_window.getch()
        self.date_win.bkgd(' ',self.black_on_white)
        date_str = ''
        
        right_format = False
        while not right_format:
            if key == KEYS['enter']:
                # initializing string
                test_str = date_str
                
                # checking if format matches the date_str
                right_format = True
                try:
                    right_format = bool(datetime.strptime(test_str, DATE_FORMAT))
                    log.info('date_str entered succesfylly')
                    
                    return date_str
                except ValueError:
                    self.print_request_message('Incorrect Date Typed')
                    right_format = False

            if key == KEYS['quit']:
                self.quit()
            
            date_str = self.draw_on_win(key,date_win,update_date,date_str)
            key = self.main_window.getch()  
            
        return date_str
   
    def handle_typing(self, window: curses.window, note: str, key: int) -> None: 
        win_r, win_c = window.getyx()
        limit = (win_r == self.big_note_height-1) and (win_c == self.big_note_width-1)
        pointer_place = win_r*(self.big_note_width)+win_c 

        if isinstance(key, str):
            key_num = ord(key)
            
            if key_num == KEYS['delete']:
                log.debug('DELETE')
                if len(note) != 0:
                    if win_c != 0:
                        window.addstr(win_r, win_c-1, ' ')
                        window.move(win_r, win_c-1)
                    elif win_c == 0 and win_r > 0:
                        window.addstr(win_r-1, self.big_note_width-1, ' ')
                        window.move(win_r-1, self.big_note_width-1)
                    if pointer_place < len(note):
                        note = note[:pointer_place] + note[pointer_place+1:]
                    elif pointer_place == len(note):
                        note = note[:-1]
                
            else:
                # handle the limit 
                if limit:
                    return note
                
                character = parse_wide_character(key)
                window.addstr(character)
                log.info(f'note before: {note}')
                if pointer_place < len(note):
                    note = note[:pointer_place] + character + note[pointer_place+1:]
                else:
                    note += character
                log.info(f'note after: {note}')
                
        elif key in KEYS['left']:
            log.debug('LEFT')
            if win_c != 0:
                window.move(win_r, win_c-1)
            elif win_c == 0 and win_r > 0:
                window.move(win_r-1, self.big_note_width-1)
                
        elif key in KEYS['right'] and not limit:
            log.debug('RIGHT')    
            
            if win_c < self.big_note_width-1:
                window.move(win_r, win_c+1)
            elif win_r < self.big_note_height:
                window = self.request_big_note_screen(window,  note)
                window.move(win_r+1, 0)
            
            if win_c > len(note):
                note += " "
        return note
        
    def note_handler(self, key, note):
        log.debug(key)
        if key in KEYS['insert']:
            log.info('insert')
            self.print_request_message('Please type in your note')
            note = self.create_note(note)
            self.print_request_message('Add request')        
        return note
    
    def request_big_note_screen(self, active_win, note):
        active_win = self.big_note_win
        active_win.clear()
        active_win.addstr(note)
        rectangle(self.main_window, 0, 0,
                    5+self.big_note_height, self.big_note_width+1)
        self.main_window.refresh()
        log.info('big_note_win')
        return active_win

    def create_note(self, note):
        curses.curs_set(0)
        
        nr = self.big_note_height
        nc = self.big_note_width
        
        limit = nr*nc - 1
        
        self.note_win.bkgd(' ',self.black_on_white)
        self.big_note_win.bkgd(' ',self.black_on_white)
        
        if note == 'Enter note...':
            note = ""
        
        if len(note) > self.big_note_width - 1:
            active_win = self.request_big_note_screen(self.note_win, note)
        else:
            active_win = self.note_win
            log.info('note_win')
        
        self.update_linewin(active_win, note, n=limit)
        key = self.main_window.get_wch()
        long = 0
        
        curses.curs_set(1)
        while not key == "\n":
            log.debug(note)
            
            if len(note) >= self.big_note_width - 1 and long == 0:
                long = 1
                
            if long == 1:
                self.print_request_message('Need more space?)')
                active_win = self.request_big_note_screen(active_win, note)
                long += 1
                        
            if len(note) > limit:
                note = note[:limit]

            log.debug(f'key:{key}')
            
            note = self.handle_typing(active_win, note, key)
            active_win.refresh()
            key = self.main_window.get_wch()
        
        curses.curs_set(0)
        for y in range(5, 5+nr+1):
            self.main_window.move(y, 0)
            self.main_window.clrtoeol()
            
        log.info('note: '+ note.replace(" ", "_"))
        return note
  
    def quit(self):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()
        exit()

        

