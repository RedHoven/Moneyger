from Screens.screen import Screen
import curses
from parsers import fill_space

class ExtendedMainScreen(Screen):
    def __init__(self, stdscr, main_screen):
        super().__init__(stdscr, main_screen.shared_state)
        
        # ingerit properties
        self.ms = main_screen
        self.shared_state = self.ms.shared_state
        self.main_window = self.ms.main_window
        self.input_win = self.ms.input_win
        
        # General screen dimensions
        self.num_rows, self.num_cols = self.stdscr.getmaxyx()
        
        # main dimensions
        self.main_width = self.ms.main_width
        self.main_height = self.ms.main_height
        
        # side space
        self.side_rows = (self.num_rows-self.main_height)//2
        self.side_cols = (self.num_cols-self.main_width)//2   
        
        # side dims
        self.side_height = 7
        self.side_width = self.main_width + 2
        
        # side windows
        self.recent_transactions_win = None
        self.num_recent = 5
        
    def draw(self):
        self.recent_transactions_win = self.stdscr.derwin(
            self.side_height, self.side_width,
            self.side_rows, self.side_cols + self.main_width) 
        
        self.info_win = self.stdscr.derwin(
            self.side_height, self.side_width,
            self.side_rows, self.side_cols - self.side_width) 
        
        self.stats_win = self.stdscr.derwin(            
            self.side_height, self.side_width*2+self.main_width,
            self.side_rows+self.side_height, self.side_cols - self.side_width) 
        
        self.recent_transactions_win.addstr(1,1,'Recent transactions:',curses.color_pair(3))
        self.info_win.addstr(1,1,'Information',curses.color_pair(3))
        self.show_recent_transactions()
        self.recent_transactions_win.box()
        self.recent_transactions_win.refresh()
        
        self.show_help()
        self.info_win.box()
        self.info_win.refresh()
        
        # self.stats_win.box()
        # self.stats_win.refresh()
        
        
    def show_recent_transactions(self):
        r,c = 2,1
        recent_ts = self.shared_state.recent_transactions
        num_to_show = min(self.num_recent, len(recent_ts))
        for i in range(num_to_show):
            self.recent_transactions_win.addstr(r+i,c, 
                                                self.format_transaction_str(recent_ts[i].to_table()))
            
    def show_help(self):
        r,c = 1,1
        self.info_win.addstr(r+1,c,'[↑][↓]  to edit spending info')
        self.info_win.addstr(r+2,c,'[←][→]  to alter category/date')
        self.info_win.addstr(r+3,c,'[i]     to edit')
        self.info_win.addstr(r+4,c,'[Enter] to confirm/add')
        
            
    def format_transaction_str(self, t_data):
        return fill_space(t_data[0], 6) + ' | ' +\
               fill_space(t_data[1], 10) + ' | ' +\
               fill_space(t_data[2], 5)
    
    def handle_input(self):
        return super().handle_input()