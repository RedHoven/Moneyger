import curses
from datetime import date, datetime, timedelta
import logging
import traceback

from database import Database, Transaction
from keys import KEYS
from state_manager import *
    
class App:
    
    def __init__(self) -> None:
        # init curses
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()                 # read input without Enter 
        self.stdscr.keypad(True)        # enable special chars
        
        # Other   
        self.init_colors()
        self.db = Database()
        self.CATEGORIES = self.db.get_categories()
        
        logging.basicConfig(filename='moneyger.log', filemode='w', level=logging.DEBUG,
                    format='%(levelname)s - %(funcName)s - %(asctime)s - %(message)s')
        self.logger = logging.getLogger(__file__)
        
        shared_state = SharedState()
        shared_state.set_logger(self.logger)
        shared_state.set_categories(self.CATEGORIES)
        shared_state.set_db(self.db)
        
        self.sm = StateManager(self.stdscr, shared_state)
        
    def init_colors(self):
        curses.start_color()
        curses.init_pair(1, curses.COLOR_MAGENTA, curses.COLOR_BLACK)   # magenta on black bg
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)    # yellow on black bg
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)     # white on black bg
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)     # green on black bg
        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_MAGENTA)   # white on magenta bg
        curses.init_pair(6,curses.COLOR_BLACK,curses.COLOR_WHITE)       # black on white bg
        curses.init_pair(7, curses.COLOR_RED, curses.COLOR_BLACK)       # red on black bg
        
    def state_handler(self, state: SharedState):
        status = state.get_state()
        
        if status == AppState.QUIT:
            self.quit()
            
        if status == AppState.MAIN:
            best_category = self.db.get_best_category()
            recent_transactions = self.get_n_recent_transaction()
            self.sm.shared_state.recent_transactions = recent_transactions
            self.sm.shared_state.transaction.category = best_category
            
        if status == AppState.SAVE_TRANSACTION:
            transaction = state.get_transaction()
            self.logger.info('saving transaction')
            # self.sync_categories(state.get_categories())
            # self.db.add_transaction(transaction)
            recent_transactions = self.get_n_recent_transaction()
            self.sm.shared_state.recent_transactions = recent_transactions
            self.logger.info(f'transaction: {state.get_transaction()}')
      
            
    def initialization(self):
        if self.sm.get_state() == AppState.INITIALIZE:
            self.sm.get_screen()
            self.state_handler(self.sm.shared_state)

    def run(self):
        try:
            self.initialization()
            while True:
                self.sm.do_transition()
                current_screen = self.sm.get_screen()
                self.logger.info(f'current screen: {current_screen}')
                current_screen.draw()
                
                state = current_screen.handle_input()
                self.state_handler(state)
                
        except Exception as e:
            self.logger.exception('\nException occurred')
        finally:
            self.logger.info("quit")
            self.quit()
                            
    def clear_wins(self):
        for w in self.windows:
            w.clear()
       
    def sync_categories(self, categories):
        self.db.update_categories(categories)    
        
    def get_n_recent_transaction(self, n = 5):
        return self.db.get_recent_transactions(n)
        
    def quit(self):
            curses.nocbreak()
            self.stdscr.keypad(False)
            curses.echo()
            curses.endwin()
            exit()