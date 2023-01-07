import curses
from curses.textpad import Textbox
from datetime import date, datetime, timedelta
import logging
from database import Database, Transactoion
from parsers import update_sum_text,update_text, update_date, update_plain_text

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
        self.db = Database()
        self.CATEGORIES = self.db.get_categories()
        
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
            
    def say(self, smth, xo=0, yo=0):
        self.stdscr.move(yo,xo)
        self.stdscr.clrtoeol()
        self.stdscr.addstr(yo,xo,smth)
        self.stdscr.refresh()
            
    def draw(self, key, processor,string):
        
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
        win.clear()
        win.addstr(new_str)
        win.refresh()
        return new_str
            
    def welcome(self):
        current_time = datetime.now()
        log.info(f"\nstarting the app: {current_time}\n")
        self.stdscr.addstr('Welcome to Moneyger!', curses.color_pair(3))

        string = ''
        sign = '-'
        sum = ''
        
        self.say('Type to add cost')
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
            if key == KEYS['enter']:
                self.say('Sum Saved. Hit ENTER to save')
                return string, False
            if key == KEYS['quit']:
                self.quit()
            elif key in KEYS['up/down']:
                if KEYS['up/down'][key] == 'up':
                    self.input_win.bkgd(' ',curses.color_pair(6))
                    self.input_win.refresh()
                elif KEYS['up/down'][key] == 'down':
                    self.input_win.bkgd(' ',curses.color_pair(3))
                    self.input_win.refresh()
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
        self.say('Add Request')
        saved = False
        self.details_win.bkgd(' ',curses.color_pair(3))
        curses.curs_set(0)
        sign = string[0]
        sum = float(string[1:])
        data = dict()
        date = datetime.now()
        date_str = datetime.now().strftime(DATE_FORMAT)
        
        # set the most probable category
        category = self.db.get_best_category()
        note = 'Enter note'
        
        data[0] = string
        data[1] = category
        data[2] = date_str 
        data[3] = note
        
        self.details_win.addstr(0,0,category)
        self.details_win.addstr(1,0,date_str)
        self.details_win.addstr(2,0,note)
        self.details_win.refresh()
        
        focus = 0
        focus_pad = curses.newpad(100,100)
        focus_pad.bkgd(' ',self.bw)
        focus_pad.addstr(0,0,category)
        focus_pad.addstr(1,0,date_str)
        focus_pad.addstr(2,0,note)
        focus_pad.refresh(focus,0,2+focus,0,2+focus,19)
        
        unfocused_pad = curses.newpad(100,100)
        unfocused_pad.bkgd(' ',curses.color_pair(3))
        unfocused_pad.addstr(0,0,category)
        unfocused_pad.addstr(1,0,date_str)
        unfocused_pad.addstr(2,0,note)

        self.stdscr.move(2,0)
        key = self.stdscr.getch()
        log.info(key)
        while True:
            
            if key == KEYS['enter']:
                #save transaction
                sign = string[0]
                sum = float(string[1:])
                transaction = Transactoion(
                    sign,
                    sum,
                    category,
                    date,
                    note
                )
                transaction.print()
                self.db.add_transaction(transaction)

                self.say('Saved!')
                key = self.stdscr.getch()
                self.say('Add Request')
                
            if key == KEYS['quit']:
                self.quit()
                
            if key in KEYS['up/down']:
                self.say('Add Request')
                if KEYS['up/down'][key] == 'down':
                    if focus == -1:
                        focus += 1
                        focus_pad.refresh(focus,0,2+focus,0,2+focus,19)
                        self.input_win.bkgd(' ',curses.color_pair(3))
                        self.input_win.refresh()
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
                        self.say('Edit Request')
                        string, down = self.handle_sum(string)
                        if down:
                            focus_pad.refresh(focus,0,2+focus,0,2+focus,19)
                            self.say('Add Request')
                        else:
                            focus = -1
                        
                        
            else:
                if focus == -1:
                    self.say('Edit Request')
                    string, down = self.handle_sum(string)
                    if down:
                        focus +=1
                        focus_pad.refresh(focus,0,2+focus,0,2+focus,19)
                    else:
                        focus = -1
                    
                if focus == 0:
                    # category field
                    category = self.сategory_handler(category, key)
    
                    data[1] = category
                    if category not in self.CATEGORIES:
                        self.CATEGORIES.append(category)  
                        self.db.add_category_to_db(category)
                        
                    log.info(self.CATEGORIES)  
                    
                    focus_pad.move(0,0)
                    focus_pad.clrtoeol()
                    focus_pad.addstr(0,0,category)
                    
                    unfocused_pad.move(0,0)
                    unfocused_pad.clrtoeol()
                    unfocused_pad.addstr(0,0,category)
                    focus_pad.refresh(focus,0,2+focus,0,2+focus,19)
                        
                if focus == 1:
                    # date_str handler
                    date_str = self.date_handler(date_str, key)
                    date = datetime.strptime(date_str, DATE_FORMAT)
                    
                    focus_pad.move(1,0)
                    focus_pad.clrtoeol()
                    focus_pad.addstr(1,0,date_str)
                    
                    unfocused_pad.move(1,0)
                    unfocused_pad.clrtoeol()
                    unfocused_pad.addstr(1,0,date_str)
                    
                    focus_pad.refresh(focus,0,2+focus,0,2+focus,19)
                
                if focus == 2:
                    # note handler
                    note = self.note_handler(key, note)
                    
                    focus_pad.move(2,0)
                    focus_pad.clrtoeol()
                    
                    unfocused_pad.move(2,0)
                    unfocused_pad.clrtoeol()
                    
                    if len(note) > 18:
                        unfocused_pad.addstr(2,0,note[:16]+"…")
                        focus_pad.addstr(2,0,note[:16]+"…")
                    else:
                        unfocused_pad.addstr(2,0,note)
                        focus_pad.addstr(2,0,note)
                        
                    focus_pad.refresh(focus,0,2+focus,0,2+focus,19)
                
            key = self.stdscr.getch()
            log.info(key)
                        
    def сategory_handler(self,category, key):
        if key in KEYS['right/left']:
            if KEYS['right/left'][key] == 'right':
                for i, c in enumerate(self.CATEGORIES):
                    if c == category and i != len(self.CATEGORIES)-1:
                        category = self.CATEGORIES[i+1]
                        break
                    elif c == category:
                        category = self.CATEGORIES[0]
                        break       
            elif KEYS['right/left'][key] == 'left':
                for i, c in enumerate(self.CATEGORIES):
                    if c == category and i != 0:
                        category = self.CATEGORIES[i-1]
                        break
                    elif c == category:
                        category = self.CATEGORIES[-1]
                        break
        elif key == KEYS['insert']:
            self.stdscr.move(0,0)
            self.stdscr.clrtoeol(); 
            self.stdscr.addstr(0,0,'Please type in new category!')
            category = self.create_category()
        elif key == KEYS['delete']:
            if len(self.CATEGORIES) != 1:
                self.delete_category(category)
                self.db.delete_category(category)
            category = self.CATEGORIES[0]
            
        return category    

    def delete_category(self,category):
        for c in self.CATEGORIES:
            if c == category:
                self.CATEGORIES.remove(category)
    
    def create_category(self):
        key = self.stdscr.getch()
        category = ''
        category_win = curses.newwin(1,20,2,0)
        category_win.bkgd(' ',self.bw)
        while key != KEYS['enter']:
            if key == KEYS['quit']:
                self.quit()
                
            category = self.draw_on_win(key,category_win,update_text,category)
            key = self.stdscr.getch()
            
        self.stdscr.move(0,0)
        self.stdscr.clrtoeol(); 
        self.stdscr.addstr(0,0,'Add Request')
        
        return category
    
    def date_handler(self, date_str, key):
        old_date = date_str
        date_win = curses.newwin(1,20,3,0)
        date_win.bkgd(' ',self.bw)
        if key in KEYS['right/left']:
            if KEYS['right/left'][key] == 'right':
                #next day    
                this_day = datetime.strptime(date_str, DATE_FORMAT)
                this_day += timedelta(days=1)
                date_str = this_day.strftime(DATE_FORMAT)
                date_str = self.draw_on_win(key,date_win,update_date,date_str)
                
            elif KEYS['right/left'][key] == 'left':
                #prev day
                this_day = datetime.strptime(date_str, DATE_FORMAT)
                this_day -= timedelta(days=1)
                date_str = this_day.strftime(DATE_FORMAT)
                date_str = self.draw_on_win(key,date_win,update_date,date_str)
                
        elif key == KEYS['insert']:
            date_str = self.create_date(date_win)
        return date_str
         
    def create_date(self, date_win):
        key = self.stdscr.getch()
        date_str = ''
        
        right_format = False
        while not right_format:
            if key == KEYS['enter']:
                log.debug('Ok, you pressed ENTER')
                
                # initializing string
                test_str = date_str
                
                # checking if format matches the date_str
                right_format = True
                try:
                    right_format = bool(datetime.strptime(test_str, DATE_FORMAT))
                    log.info('date_str entered succesfylly')
                    self.stdscr.move(0,0)
                    self.stdscr.clrtoeol(); 
                    self.stdscr.addstr(0,0,'Add Request')
                    return date_str
                except ValueError:
                    self.stdscr.move(0,0)
                    self.stdscr.clrtoeol(); 
                    self.stdscr.addstr(0,0,'Incorrect Date Typed')
                    right_format = False

            if key == KEYS['quit']:
                self.quit()
            
            date_str = self.draw_on_win(key,date_win,update_date,date_str)
            key = self.stdscr.getch()
            
    
        return date_str
   
    def note_handler(self, key, note):
        note_win = curses.newwin(1,20,4,0)
        note_win.bkgd(' ',self.bw)
        
        log.debug(key)
        if key == KEYS['insert']:
            log.info('insert')
            self.stdscr.move(0,0)
            self.stdscr.clrtoeol(); 
            self.stdscr.addstr(0,0,'Please type in your note')
            note = self.create_note(note_win, note)
            self.stdscr.move(0,0)
            self.stdscr.clrtoeol(); 
            self.stdscr.addstr(0,0,'Add request')
        
        if key == 136:
            log.info('insert')
            self.stdscr.move(0,0)
            self.stdscr.clrtoeol(); 
            self.stdscr.addstr(0,0,'Please type in your note')
            note = self.create_note(note_win, note)
            self.stdscr.move(0,0)
            self.stdscr.clrtoeol(); 
            self.stdscr.addstr(0,0,'Add request')
        
        return note
    
    def create_note(self,note_win, note):
        curses.curs_set(2)
        self.stdscr.move(4,len(note))
        big_note_win = curses.newwin(10,40,4,0)
        big_note_win.bkgd(' ',curses.color_pair(6))
        
        if len(note) > 18:
            active_win = big_note_win
        else:
            active_win = note_win
        
        active_win.clear()
        active_win.addstr(note)
        active_win.bkgd(' ',curses.color_pair(6))   
        active_win.refresh()
        key = self.stdscr.get_wch()
        while not isinstance(key, int) and not key in ('\n'):
            if len(note) > 18:
                active_win = big_note_win
                
            if key in ('KEY_BACKSPACE', '\b', '\x7f'):
                note = update_plain_text(note,key,True)
            else:
                note = update_plain_text(note,key)
                log.info(key)
                
            active_win.clear()
            try:
                active_win.addstr(note)
            except curses.error:
                log.error(curses.error.__name__)
            active_win.refresh()
            key = self.stdscr.get_wch()    
            log.debug(key)
        
        big_note_win.clear()
        big_note_win.bkgd(' ',curses.color_pair(3)) 
        big_note_win.refresh()
        self.stdscr.refresh()
        log.info('note: '+ note)
        curses.curs_set(0)
        return note
  
    def quit(self):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()
        exit()

        

