from numpy import block
from Screens.screen import Screen
import curses
from parsers import fill_space
from state import SharedState, AppState
from stats import Statistics
from keys import KEYS
from curses.textpad import rectangle

class AnalysisScreen(Screen):
    def __init__(self, stdscr, shared_state):
        super().__init__(stdscr, shared_state)
        
        # inherit properties
        self.shared_state = shared_state
        self.logger = self.shared_state.get_logger()
        
        # General screen dimensions
        self.num_rows, self.num_cols = self.stdscr.getmaxyx()
        
        # main dimensions
        self.main_width = 80
        self.main_height = 30
        
        # start coords
        self.s_rows = (self.num_rows-self.main_height)//2
        self.s_cols = (self.num_cols-self.main_width)//2   
        
        # side windows
        self.recent_transactions_win = None
        self.num_recent = 5
        self.stats = None
    
    def initialize(self):
        if self.main_width > self.num_cols or self.main_height > self.num_rows:
            self.logger.info('Returning back the app because of too small window')
            self.shared_state.set_state(AppState.BACK)
        else:
            self.logger.info('Returning analysis window')
            self.shared_state.set_state(AppState.ANALYSIS)
            self.stats = Statistics(self.shared_state.db)
            
        
    def draw(self):
        self.stdscr.clear()
        self.analysis_screen = self.stdscr.derwin(
            self.main_height, self.main_width,
            self.s_rows, self.s_cols)
        headline = 'Statistics'
        self.analysis_screen.addstr(1, 1+(self.main_width-len(headline))//2, headline)
        self.show_stats()
        self.analysis_screen.box()
        self.analysis_screen.refresh()
        
    def show_stats(self):
        r,c = 2,1
        center_block_width = 30
        self.logger.info(self.stats.current_month)
        data_this = self.stats.get_month_stats()
        data_prev = self.stats.get_month_stats(1)
        summary_data = self.stats.get_summary()
        space = '  ' if data_this['total_spent'] < 100 else ''
        this_month_headline = f'This Month Total Spent: {data_this["total_spent"]}'
        prev_month_headline = 'Previous Month Highlights'
        summary_headline = 'Summary'
        this_month_col = len(this_month_headline)
        prev_month_col = len(prev_month_headline)
        self.analysis_screen.addstr(r, c+(self.main_width-len(this_month_headline))//2, this_month_headline)
        
        # previous month
        self.analysis_screen.addstr(r+2, c+(self.main_width-prev_month_col)//2, prev_month_headline)
        
        if data_prev["total_profit"] > 0:
            color = curses.color_pair(4) # green
            space = ' '
        else:
            color = curses.color_pair(7) # red
            space = ''
        
        self.analysis_screen.addstr(r+3,(c+self.main_width-center_block_width)//2,f'Total Spent:\t\t')
        self.analysis_screen.addstr(f'-{data_prev["total_spent"]}')
        self.analysis_screen.addstr(r+4,(c+self.main_width-center_block_width)//2,f'Profit:\t\t')
        self.analysis_screen.addstr(f'{space}{data_prev["total_profit"]}',color)
        
        blocksize = (self.main_width - 4)//2
        
        rectangle(self.analysis_screen, r+5, 1,
            r+5+7, blocksize)
        rectangle(self.analysis_screen, r+5, blocksize+1,
            r+5+7, self.main_width-2)
        
        
        self.analysis_screen.addstr(r+6,c+1,'Spent per category last month')
        self.analysis_screen.addstr(r+6,c+blocksize+1,'Average spent per category per month')
        
        top_exp = list(zip(data_prev["top_spendings"].keys(), data_prev["top_spendings"].values()))
        top_num = len(top_exp)
        top_freq = list(zip(summary_data["category_per_month"].keys(), summary_data["category_per_month"].values()))
        
        for i in range(top_num):
            self.analysis_screen.addstr(r+7+i,c+7,fill_space(f'{top_exp[i][0]}',20)+f'{round(top_exp[i][1],2)}')
            self.analysis_screen.addstr(r+7+i,c+7+blocksize+1,fill_space(f'{top_freq[i][0]}',20)+f'{round(top_freq[i][1],2)}')
            
        self.analysis_screen.addstr(r+14,c+(self.main_width - len(summary_headline))//2,summary_headline)
        
        spendings_per_month = list(zip(summary_data['spendings_per_month'].keys(), summary_data['spendings_per_month'].values()))
        avg_per_month_txt = f'Average spent per month: {round(summary_data["avg_spendings_per_month"],2)} EUR'
        self.analysis_screen.addstr(r+15,c+(self.main_width-len(avg_per_month_txt))//2, avg_per_month_txt)
        self.analysis_screen.addstr(r+17,c+(self.main_width-center_block_width)//2,fill_space(f'month',20)+f'EUR')
        for i in range(6):
            self.analysis_screen.addstr(r+18+i,c+(self.main_width-center_block_width)//2,fill_space(f'{spendings_per_month[5-i][0]}',20)+f'{round(spendings_per_month[5-i][1],2)}')
                
    def handle_input(self):
        key = self.analysis_screen.getch()
        if key == KEYS['quit']:
            self.shared_state.set_state(AppState.QUIT)
        if key == KEYS['transaction']:
            self.shared_state.set_state(AppState.TRANSACTION)
            self.analysis_screen.clear()
            self.analysis_screen.refresh()
        return self.shared_state