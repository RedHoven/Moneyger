from re import A
from Screens.main_screen import *
    
class StateManager:
    def __init__(self, stdscr, shared_state):
            self.stdscr = stdscr
            self.logger = shared_state.get_logger()
            self.shared_state = shared_state
            self.screens = {}
            self.transitions = {
                AppState.QUIT: AppState.QUIT,
                AppState.INITIALIZATION : AppState.MAIN_SCREEN,
                AppState.MAIN_SCREEN: AppState.WELCOME_SCREEN,
                AppState.WELCOME_SCREEN: AppState.TRANSACTION_SCREEN,
                AppState.TRANSACTION_SCREEN : AppState.TRANSACTION_SCREEN,
                AppState.SAVE_TRANSACTION: AppState.TRANSACTION_SCREEN_SAVED
            }
            
    def transition(self, current_state):
        return self.transitions[current_state]
    
    def set_state(self, new_state):
        self.shared_state.set_state(new_state)
        
    def get_state(self):
        return self.shared_state.get_state()
    
    def get_shared_state(self) -> SharedState:
        return self.shared_state

    def get_current_screen(self):
        self.do_transition()
        screen = self.screens.get(self.get_state())
        if not screen:
            screen = self.create_screen()
            current_state = self.get_state()
            self.screens[self.get_state()] = screen
        
        self.logger.info('AppState: '+str(self.get_state()))
        return screen
    
    def do_transition(self):
        self.set_state(self.transition(self.get_state()))
    
    def create_screen(self):
        if self.get_state() == AppState.MAIN_SCREEN:
            screen = MainScreen(self.stdscr, self.shared_state)
            self.shared_state = screen.initialize()
            return screen
        if self.get_state() == AppState.WELCOME_SCREEN:
            return WelcomeScreen(self.stdscr, self.screens[AppState.MAIN_SCREEN])
        
        if self.get_state() == AppState.TRANSACTION_SCREEN:
            return TransactionScreen(self.stdscr, self.screens[AppState.MAIN_SCREEN])
        
        if self.get_state() == AppState.TRANSACTION_SCREEN_SAVED:
            return self.screens[AppState.TRANSACTION_SCREEN]