from enum import Enum
from database import Transaction
from datetime import datetime

class AppState:
    QUIT = "quit"
    WELCOME = "welcome"
    TRANSACTION = "transaction"
    PROFILE = "profile"
    ANALYSIS = "analysis"
    SAVE = "save" 
    INITIALIZE = "initialize"
    MAIN = "main"
    SAVE_TRANSACTION = "transaction_saved"
    EXT_MAIN = "ext_main"
    BACK = "back"
    
class SharedState:
    def __init__(self):
        self.current_state = AppState.INITIALIZE
        self.transaction = Transaction(sign='-',sum=0.0,category='',date=datetime.now(),note='')
        self.logger = None
        self.current_key = None
        self.categories = None
        self.recent_transactions = []
        self.state_history = []
        self.db = None
        
    def revert_state(self) -> AppState:
        self.logger.info(self.state_history)
        if self.state_history[-1] == self.state_history[-2]:
            self.state_history = self.state_history[:-1]
            self.revert_state()
        else:
            self.state_history = self.state_history[:-2]
            self.current_state = self.state_history[-1]
            return self.get_state()
        
    def set_db(self, db):
        self.db = db
        
    def set_categories(self, categories: list):
        self.categories = categories
        
    def get_categories(self) -> list:
        return self.categories
    
    def set_recent_transactions(self, recent_transactions: list):
        self.recent_transactions = recent_transactions
        
    def get_recent_transactions(self) -> list:
        return self.recent_transactions
        
    def set_logger(self, logger):
        self.logger = logger 
        
    def get_logger(self):
        return self.logger   
    
    def set_state(self, new_state: AppState) -> None:
        if new_state != self.get_state():
            self.state_history.append(new_state)
        self.current_state = new_state
        
    def get_state(self) -> AppState:
        return self.current_state
    
    def set_transaction(self, transaction: Transaction) -> None:
        self.transaction = transaction
        
    def get_transaction(self) -> Transaction:
        return self.transaction
    
    def __str__(self) -> str:
        return f"Shared Stage: \nstate: {self.current_state}, \ntransaction: {self.transaction.to_rowstr()}, \nlen of recent transactions: {len(self.recent_transactions)}"