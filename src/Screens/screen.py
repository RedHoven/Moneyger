from abc import ABC, abstractmethod
from state import SharedState
import curses

class Screen(ABC):
    def __init__(self, stdscr: curses.window, shared_state: SharedState):
        self.stdscr = stdscr
        self.shared_state = shared_state

    @abstractmethod
    def draw(self) -> None:
        pass

    @abstractmethod
    def handle_input(self) -> SharedState:
        pass