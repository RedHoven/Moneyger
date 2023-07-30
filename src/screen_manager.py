from state import AppState

from Screens.analysis_screen import AnalysisScreen
from Screens.extended_screen import ExtendedMainScreen
from Screens.main_screen import *

class ScreenFactory:
    def __init__(self, stdscr, shared_state):
        self.stdscr = stdscr
        self.shared_state = shared_state
        self.screens = {}

    def get_screen(self):
        state = self.shared_state.get_state()
        if state in self.screens:
            return self.screens[state]

        screen = None
        if state == AppState.INITIALIZE:
            screen = MainScreen(self.stdscr, self.shared_state)
            self.shared_state = screen.initialize()
            ext_screen = ExtendedMainScreen(self.stdscr, screen)
            self.screens[AppState.EXT_MAIN] = ext_screen
            self.screens[AppState.MAIN] = screen

        elif state == AppState.WELCOME:
            screen = WelcomeScreen(self.stdscr, self.screens[AppState.MAIN])

        elif state == AppState.TRANSACTION:
            screen = TransactionScreen(self.stdscr, self.screens[AppState.EXT_MAIN])

        elif state == AppState.SAVE_TRANSACTION:
            screen = self.screens[AppState.TRANSACTION]

        elif state == AppState.ANALYSIS:
            screen = AnalysisScreen(self.stdscr, self.shared_state)
            screen.initialize()
            
        if screen:
            self.screens[self.shared_state.get_state()] = screen
            
        return screen