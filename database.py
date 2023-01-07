from datetime import datetime
import logging
import sqlite3
from sqlite3 import Error

class Transactoion:
    def __init__(self, sign: str, sum: float, category: str, date: datetime, note: str) -> None:
        self.sign = sign
        self.sum = sum
        self.category = category
        self.date = date
        self.note = note
        
        logging.basicConfig(filename='transactions.log', filemode='w', level=logging.DEBUG)
        self.log = logging.getLogger(__file__)
    
    def print(self):
        self.log.info(
            '\n'+"Transaction Info"+'\n'+\
            "Sign: "+ self.sign +'\n'+\
            "sum: "+ str(self.sum) +'\n'+\
            "category: "+ self.category +'\n'+\
            "date: "+ str(self.date) +'\n'+\
            "note: "+ self.note
        )
        
class Database():
    def __init__(self):
        self.connect_to_db()
        self.create_tables()
    
    def connect_to_db(self):
        self.connection = sqlite3.connect('moneyger.db')
        self.cursor = self.connection.cursor()
        
    def create_tables(self):
        c = self.cursor
        c.execute('''
                CREATE TABLE IF NOT EXISTS 
                Transactions
                ([transaction_id] INTEGER PRIMARY KEY AUTOINCREMENT, 
                [sign] TEXT,
                [sum] REAL,
                [category] TEXT,
                [date] TEXT,
                [note] TEXT)
                ''')
          
        c.execute('''
                CREATE TABLE IF NOT EXISTS 
                Categories
                ([category_id] INTEGER PRIMARY KEY AUTOINCREMENT, 
                [name] TEXT,
                [frequency] INTEGER DEFAULT 0)
                ''')
        
        self.connection.commit()
        
        
    def add_category_to_db(self, category):
        self.cursor.execute(
            '''
            INSERT INTO Categories(name,frequency) VALUES("%s","%s")
            ''' % (category, 0)
        )
        self.connection.commit()
        
    def update_categories(self, list):
        c = self.cursor
        for item in list:
            c.execute("SELECT * FROM Categories WHERE name=?", (item,))
            category = c.fetchall()
            if len(category) == 0:
                self.add_category_to_db(item)         
    
    def get_categories(self):
        c = self.cursor
        c.execute("SELECT * FROM Categories")
        category_list = c.fetchall()
        list = []
        for i in category_list:
            list.append(i[1])
        
        return list
    
    def add_transaction(self, t:Transactoion):
        # ensure category exists
        self.update_categories((t.category,))
        
        c = self.cursor
        c.execute("INSERT INTO Transactions(sign,sum,category,date,note) VALUES (?,?,?,?,?)",
                  (t.sign, t.sum, t.category, t.date, t.note))
        c.execute("SELECT * FROM Categories WHERE name=?",(t.category,))
        cur_cat_freq = c.fetchall()
        c.execute("UPDATE Categories SET frequency=? WHERE name=?",(cur_cat_freq[0][2]+1,t.category))
        self.connection.commit()
        
    def clear_table(self, table):
        c = self.cursor
        c.execute("DELETE FROM "+table)
        self.connection.commit()
        
    def clear_tables(self):
        c = self.cursor
        c.execute("UPDATE Categories SET frequency=0")
        c.execute("DELETE FROM Transactions")
        self.connection.commit()
        
    def get_best_category(self):
        c = self.cursor
        c.execute("SELECT * FROM Categories ORDER BY frequency DESC")
        categories = c.fetchall()
        best_one = categories[0][1]
        return best_one
    
    def delete_category(self, name):
        c = self.cursor
        c.execute('DELETE FROM Categories WHERE name=?',(name,))
        self.connection.commit()

if __name__ == "__main__":
    d = Database()
    d.clear_tables()
    d.update_categories(['groceries','restaurants','presents'])
    d.connection.commit()