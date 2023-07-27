from abc import ABC, abstractmethod

class Screen(ABC):
    def __init__(self, stdscr, shared_state):
        self.stdscr = stdscr
        self.shared_state = shared_state

    @abstractmethod
    def draw(self):
        pass

    @abstractmethod
    def handle_input(self):
        pass