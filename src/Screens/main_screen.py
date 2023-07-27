from re import S
from Screens.screen import Screen
import curses
from curses.textpad import rectangle
from datetime import date, datetime, timedelta
from parsers import *

from keys import KEYS
from database import Database, Transaction
from state import AppState, SharedState

class MainScreen(Screen):
    def __init__(self, stdscr, shared_state: SharedState):
        super().__init__(stdscr, shared_state)
        
        self.logger = shared_state.get_logger()
        self.transaction = shared_state.get_transaction()
        self.shared_state = shared_state
        self.stdscr = stdscr
        
        # General screen dimensions
        self.num_rows, self.num_cols = self.stdscr.getmaxyx()
        
        # App dimensions
        self.main_width = 30
        self.main_height = 20 
            
        self.main_window = None
        self.input_win = None
        
        # upper left corner of the main window
        self.col_s = (self.num_cols-self.main_width)//2
        self.row_s = (self.num_rows-self.main_height)//2
        
        # starting position of a details window message line
        self.details_msg_coords = (self.row_s+1, self.col_s+1)
        
        # set main colors
        self.white_on_black = curses.color_pair(3)
        self.black_on_white = curses.color_pair(6)

    def initialize(self):
        if self.main_width > self.num_cols or self.main_height > self.num_rows:
            self.logger.info('Closing the app because of too small window')
            self.shared_state.set_state(AppState.QUIT)
            return self.shared_state
        
        self.main_window = self.stdscr.derwin(self.main_height,
                            self.main_width,
                            (self.num_rows-self.main_height)//2,
                            (self.num_cols-self.main_width)//2)
        
        # self.main_window.keypad(True)        # enable special chars for main win
        self.input_win = self.main_window.derwin(1, self.main_width-2, 2, 1)
        self.shared_state.set_state(AppState.MAIN_SCREEN)
        return self.shared_state
    
    def draw(self):
        pass
    
    def handle_input(self):
        pass
    
    def process_string(self, key, processor ,string):
        if key == KEYS['delete']:
            new_str = processor(string,chr(key),True)
        else:
            new_str = processor(string,chr(key))
        return new_str
    
    def cut_string(self, string, n=None):
        if n is None:
            n = self.main_width-3
        processed_str = string
        if len(string) > n:
            processed_str = string[:n]
        return processed_str
    
    def update_linewin(self, linewin, message, n=None, refresh=True):
        linewin.clear()
        linewin.addstr(self.cut_string(message, n=n))
        if refresh:
            linewin.refresh()
    
    def sum_handler(self, key, highlight=False):
        t: Transaction = self.transaction
        sign: str = t.sign
        sum: str = str(t.sum)
            
        string = sign + sum 
        previous_str = string
        
        if highlight:
            self.input_win.bkgd(' ',self.black_on_white)
        else:
            self.input_win.bkgd(' ',self.white_on_black)
        
        while True:            
            if (key == KEYS['enter'] or key in KEYS['down']) and not sum=='':
                self.transaction.sign = sign
                self.transaction.sum = float(sum)
                self.shared_state.current_key = key
                self.shared_state.set_state(AppState.TRANSACTION_SCREEN)
                return
            
            if key == KEYS['quit']:
                self.shared_state.set_state(AppState.QUIT)
                return
            
            if key == KEYS['plus']:
                sign = '+'
            elif key == KEYS['minus']:
                sign = '-' 
            else:
                sum = self.process_string(key,update_sum_text,sum)
                
            string = sign + sum
            if previous_str != string:
                previous_str = string
                self.update_linewin(self.input_win, self.cut_string(string))
            self.stdscr.refresh()
            key = self.stdscr.getch()
    
class ExtendedMainScreen(Screen):
    def __init__(self, stdscr, shared_state):
        super().__init__(stdscr, shared_state)
        
        # side space
        self.side_rows = (self.num_rows-self.main_height)//2
        self.side_cols = (self.num_cols-self.main_width)//2   
        
        self.recent_transactions_win = curses.newwin(self.side_height, self.side_width,
                                                self.side_height, self.side_width + self.main_width) 

class WelcomeScreen(Screen):
    def __init__(self, stdscr, main_screen):
        super().__init__(stdscr, main_screen.shared_state)
        self.ms = main_screen
        self.shared_state = self.ms.shared_state
        self.welcome_win = self.ms.main_window.derwin(5,self.ms.main_width, 0, 0)
        self.input_win = self.ms.input_win
        
    def welcome(self, key):
        self.ms.sum_handler(key)
        return self.shared_state
        
    def draw(self):
        self.welcome_win.addstr(1,1,'Welcome to Moneyger!')
        self.input_win.addstr('Type in the cost')
        self.input_win.refresh()
        
        self.welcome_win.box()
        self.welcome_win.refresh()
        curses.curs_set(0)
        
    def handle_input(self):
        super().handle_input()
        key = self.stdscr.getch()
        return self.welcome(key)

class TransactionScreen(Screen):
    
    DATE_FORMAT = "%d-%m-%Y"
    
    def __init__(self, stdscr, main_screen):
        super().__init__(stdscr, main_screen.shared_state)
        self.ms = main_screen
        self.main_window = self.ms.main_window
        self.shared_state = self.ms.shared_state
        self.t: Transaction = self.shared_state.get_transaction()
        self.log = self.shared_state.get_logger()
        self.CATEGORIES = self.shared_state.get_categories()
        
        # main dimensions
        self.main_width = self.ms.main_width
        self.main_height = self.ms.main_height
        
        # other dimensions
        self.big_note_height = self.main_height - 17
        self.big_note_width  = self.main_width - 2
        
        # pad init
        self.focus = 1
        self.focus_pad = None
        self.unfocused_pad = None
        
        # colors
        self.black_on_white = self.ms.black_on_white
        self.white_on_black = self.ms.white_on_black
        
        # starting left upper corner coords
        self.col_s = self.ms.col_s
        self.row_s = self.ms.row_s
        
    def draw(self):
        self.input_win = self.ms.input_win
        self.category_win = self.main_window.derwin(1, self.main_width-2, 3, 1)
        self.date_win = self.main_window.derwin(1, self.main_width-2, 4, 1)
        self.note_win = self.main_window.derwin(1, self.big_note_width, 5, 1)
        self.big_note_win = self.main_window.derwin(self.big_note_height, self.big_note_width, 5, 1)
        self.details_win = self.main_window.derwin(7, self.main_width, 0, 0)
        
        # Init blank details win
        self.stdscr.clear()
        self.stdscr.bkgd(' ', curses.color_pair(3))
        self.details_win.box()
        if self.shared_state.get_state() == AppState.TRANSACTION_SCREEN:
            self.print_request_message('Add Request')
        elif self.shared_state.get_state() == AppState.TRANSACTION_SCREEN_SAVED:
            self.print_request_message('Saved!')
        
        sign = self.t.sign
        sum = self.t.sum
        date = self.t.date
        date_str = self.t.date.strftime(self.DATE_FORMAT)
        string = sign + str(sum)
        
        # set the most probable category
        category = self.t.category
        note = 'Enter note...'
        self.t.note = note
        
        self.details_win.addstr(2,1,string)
        self.details_win.addstr(3,1,category)
        self.details_win.addstr(4,1,date_str)
        self.details_win.addstr(5,1,note)
        self.details_win.refresh()

        self.focus = 1    # initialize cursor on category
        self.focus_pad = curses.newpad(7,self.main_width)
        self.focus_pad.bkgd(' ',self.black_on_white)
        self.focus_pad.addstr(2,0,string)
        self.focus_pad.addstr(3,0,category)
        self.focus_pad.addstr(4,0,date_str)
        self.focus_pad.addstr(5,0,note)
        self.refresh_pad(self.focus_pad, self.focus)
        
        self.unfocused_pad = curses.newpad(7,self.main_width)
        self.unfocused_pad.bkgd(' ',curses.color_pair(3))
        self.unfocused_pad.addstr(2,0,string)
        self.unfocused_pad.addstr(3,0,category)
        self.unfocused_pad.addstr(4,0,date_str)
        self.unfocused_pad.addstr(5,0,note)
        
    def handle_input(self):
        super().handle_input()
        key = self.focus_pad.getch()
        self.main_window.refresh()
        state = self.add_request(key)
        return state
               
    def print_request_message(self, message):
        r,c = 1,1
        self.details_win.addstr(r,c," "*(self.main_width-3))
        self.details_win.addstr(r,c, message)
        self.details_win.refresh()
            
    def draw_on_win(self,key, win, processor,string):
        if key == KEYS['delete']:
            new_str = processor(string,chr(key),True)
        else:
            new_str = processor(string,chr(key))
        self.ms.update_linewin(win, new_str)
        return new_str
    
    def refresh_pad(self, pad, focus, type='focused', direction='down', x= None, y= None):    
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
        
    def add_request(self, key):
        focus = self.focus
        focus_pad = self.focus_pad
        unfocused_pad = self.unfocused_pad
        
        # transaction info
        sign = self.t.sign
        sum = self.t.sum
        category = self.t.category
        date = self.t.date
        note = self.t.note
        date_str = self.t.date.strftime(self.DATE_FORMAT)
        string = sign + str(sum)
        
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
                self.shared_state.set_transaction(transaction)
                self.shared_state.set_state(AppState.SAVE_TRANSACTION)
                self.shared_state.set_categories(self.CATEGORIES)

                self.print_request_message('Saved!')
                self.log.info('SAVED')
                if focus == -1:
                    self.input_win.bkgd(' ',curses.color_pair(6))
                    self.input_win.refresh()
                else:
                    self.refresh_pad(focus_pad, focus)
                return self.shared_state              
            elif key == KEYS['quit']:
                self.shared_state.set_state(AppState.QUIT)
                return self.shared_state  
            
            elif key in KEYS['up/down']:
                self.log.info('Up/down')
                
                if key in KEYS['down']:
                    self.log.info('down')
                    self.log.debug('focus: '+str(focus))
                    self.log.debug('category: '+ category)
                    
                    if focus < 3:
                        focus += 1
                        self.refresh_pad(unfocused_pad, focus, 'unfocused')
                        self.refresh_pad(focus_pad, focus)
                        self.print_focus_message(focus)
                        
                if key in KEYS['up']:
                    self.log.info('up')
                    if focus > 0:
                        focus -= 1
                        self.refresh_pad(unfocused_pad, focus, 'unfocused','up')
                        self.refresh_pad(focus_pad, focus)
                        self.print_focus_message(focus)
                      
            else:
                if focus == 0:
                    self.ms.sum_handler(key, True)
                    string = self.shared_state.transaction.sign + str(self.shared_state.transaction.sum)
                    down = self.shared_state.current_key in KEYS['down']
                    
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
                        
                    self.log.info(self.CATEGORIES)  
                    
                    if previous_category != category:
                        self.category_win.bkgd(' ',self.white_on_black)
                        self.category_win.refresh()
                        
                        focus_pad.move(3,0)
                        focus_pad.clrtoeol()
                        focus_pad.addstr(3,0,category)
                        
                        unfocused_pad.move(3,0)
                        unfocused_pad.clrtoeol()
                        unfocused_pad.addstr(3,0,category)
                        
                        self.ms.update_linewin(self.category_win, category, refresh=False)
                        self.refresh_pad(focus_pad, focus)
                        
                elif focus == 2:
                    previous_date = date_str
                    date_str = self.date_handler(date_str, key, focus_pad)
                    if date_str is None:
                        return self.shared_state
                    date = datetime.strptime(date_str, self.DATE_FORMAT)
 
                    if previous_date != date_str:
                        self.date_win.bkgd(' ',self.white_on_black)
                        self.date_win.refresh()
                        
                        focus_pad.move(4,0)
                        focus_pad.clrtoeol()
                        focus_pad.addstr(4,0,date_str)
                        
                        unfocused_pad.move(4,0)
                        unfocused_pad.clrtoeol()
                        unfocused_pad.addstr(4,0,date_str)
                        self.ms.update_linewin(self.date_win, date_str, refresh=False)
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
                        self.log.info(len(note))
                        self.note_win.addstr(0, 0,note)
                        unfocused_pad.addstr(5,0,note)
                        focus_pad.addstr(5,0,note)
                        
                    # restore the box  
                    self.details_win.box()
                    self.details_win.refresh()
                    self.main_window.refresh()
                        
                    self.refresh_pad(unfocused_pad, focus, 'unfocused')
                    self.refresh_pad(focus_pad, focus)
                  
            key = self.stdscr.getch()
            self.log.info(key)
       
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
            self.log.info('No such category')
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
            this_day = datetime.strptime(date_str, self.DATE_FORMAT)
            this_day += timedelta(days=1)
            date_str = this_day.strftime(self.DATE_FORMAT)
            date_str = self.draw_on_win(key,self.date_win,update_date,date_str)
            
        elif key in KEYS['left']:
            #prev day
            this_day = datetime.strptime(date_str, self.DATE_FORMAT)
            this_day -= timedelta(days=1)
            date_str = this_day.strftime(self.DATE_FORMAT)
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
                    right_format = bool(datetime.strptime(test_str, self.DATE_FORMAT))
                    self.log.info('date_str entered succesfylly')
                    
                    return date_str
                except ValueError:
                    self.print_request_message('Incorrect Date Typed')
                    right_format = False

            if key == KEYS['quit']:
                self.shared_state.set_state(AppState.QUIT)
                return None
            
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
                self.log.debug('DELETE')
                if len(note) != 0:
                    if win_c != 0:
                        window.addstr(win_r, win_c-1, ' ')
                        window.move(win_r, win_c-1)
                    elif win_c == 0 and win_r > 0:
                        window.addstr(win_r-1, self.big_note_width-1, ' ')
                        window.move(win_r-1, self.big_note_width-1)
                    if pointer_place < len(note):
                        note = note[:pointer_place] + ' ' + note[pointer_place+1:]
                    elif pointer_place == len(note):
                        note = note[:-1]
                
            else:
                # handle the limit 
                if limit:
                    return note
                
                character = parse_wide_character(key)
                window.addstr(character)
                self.log.info(f'note before: {note}')
                if pointer_place < len(note):
                    note = note[:pointer_place] + character + note[pointer_place+1:]
                else:
                    note += character
                self.log.info(f'note after: {note}')
                
        elif key in KEYS['left']:
            self.log.debug('LEFT')
            if win_c != 0:
                window.move(win_r, win_c-1)
            elif win_c == 0 and win_r > 0:
                window.move(win_r-1, self.big_note_width-1)
                
        elif key in KEYS['right'] and not limit:
            self.log.debug('RIGHT')    
            
            if win_c < self.big_note_width-1:
                window.move(win_r, win_c+1)
            elif win_r < self.big_note_height:
                window = self.request_big_note_screen(window,  note)
                window.move(win_r+1, 0)
            
            if win_c > len(note):
                note += " "
        return note
        
    def note_handler(self, key, note):
        self.log.debug(key)
        if key in KEYS['insert']:
            self.log.info('insert')
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
        self.log.info('big_note_win')
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
            self.log.info('note_win')
        
        self.ms.update_linewin(active_win, note, n=limit)
        key = self.stdscr.get_wch()
        long = 0
        
        curses.curs_set(1)
        while not key == "\n":
            self.log.debug(note)
            
            if len(note) >= self.big_note_width - 1 and long == 0:
                long = 1
                
            if long == 1:
                self.print_request_message('Need more space?)')
                active_win = self.request_big_note_screen(active_win, note)
                long += 1
                        
            if len(note) > limit:
                note = note[:limit]

            self.log.debug(f'key:{key}')
            
            note = self.handle_typing(active_win, note, key)
            active_win.refresh()
            key = self.stdscr.get_wch()
        
        curses.curs_set(0)
        for y in range(5, 5+nr+1):
            self.main_window.move(y, 0)
            self.main_window.clrtoeol()
            
        self.log.info('note: '+ note.replace(" ", "_"))
        return note


        

