from enum import Enum
from database import Transaction
from datetime import datetime

class AppState(Enum):
    QUIT = 0
    WELCOME_SCREEN = 1
    TRANSACTION_SCREEN = 2
    PROFILE_SCREEN = 3
    ANALYSIS_SCREEN = 4
    SAVE_TRANSACTION = 5
    INITIALIZATION = 6
    MAIN_SCREEN = 7
    TRANSACTION_SCREEN_SAVED = 8
    
class SharedState:
    def __init__(self):
        self.current_state = AppState.INITIALIZATION
        self.transaction = Transaction(sign='-',sum=0.0,category='',date=datetime.now(),note='')
        self.logger = None
        self.current_key = None
        self.categories = None
        
    def set_categories(self, categories: list):
        self.categories = categories
        
    def get_categories(self) -> list:
        return self.categories
        
    def set_logger(self, logger):
        self.logger = logger 
        
    def get_logger(self):
        return self.logger   
    
    def set_state(self, new_state: AppState) -> None:
        self.current_state = new_state
        
    def get_state(self) -> AppState:
        return self.current_state
    
    def set_transaction(self, transaction: Transaction) -> None:
        self.transaction = transaction
        
    def get_transaction(self) -> Transaction:
        return self.transaction