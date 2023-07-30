from state import AppState, SharedState
from screen_manager import ScreenFactory
from Screens.screen import Screen

class StateManager:
    def __init__(self, stdscr, shared_state):
            self.stdscr = stdscr
            self.logger = shared_state.get_logger()
            self.shared_state = shared_state
            self.factory = ScreenFactory(self.stdscr, self.shared_state)
            self.screens = {}
            self.transitions = {
                AppState.QUIT: AppState.QUIT,
                AppState.MAIN: AppState.WELCOME,
                AppState.WELCOME: AppState.TRANSACTION
            }
            
    def transition(self, current_state):
        if current_state in self.transitions:
            return self.transitions[current_state]
        return current_state
    
    def set_state(self, new_state):
        self.shared_state.set_state(new_state)
        
    def get_state(self):
        return self.shared_state.get_state()
    
    def do_transition(self):
        self.logger.info(f'{self.get_state()}')
        self.set_state(self.transition(self.get_state()))
        self.logger.info(f'{self.get_state()}')
        
    def get_screen(self) -> Screen:
        screen = self.factory.get_screen()
        if self.get_state() == AppState.BACK:
            state = self.shared_state.revert_state()
            screen = self.factory.get_screen()
            self.logger.info(self.shared_state.state_history)
        return screen