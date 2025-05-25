from datetime import datetime
import logging
import sqlite3
from sqlite3 import Error
import pandas as pd
from utils import DATE_FORMAT

class Transaction:
    
    def __init__(self, sign: str, sum: float, category: str, date: datetime, note: str) -> None:
        self.sign = sign
        self.sum = sum
        self.category = category
        self.date = date
        self.note = note
        self.log = None
        self.string = None
        
    def init_logger(self, logger):
        self.log = logger

    def __str__(self):
        return '\n' + "Transaction Info" + '\n' + \
                "sign: " + self.sign + '\n' + \
                "sum: " + str(self.sum) + '\n' + \
                "category: " + self.category + '\n' + \
                "date: " + str(self.date) + '\n' + \
                "note: " + self.note
                
    def to_rowstr(self):
        return f"{self.sign+str(self.sum)}\t {self.category}\t {self.date.strftime('%d-%m')}"
    
    def to_table(self):
        return  self.sign+str(self.sum),\
                self.category,\
                self.date.strftime('%d-%m')
                
    def set_str(self, string):
        self.string = string
    

class Database:
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
                [frequency] INTEGER DEFAULT 0,
                [hide] INTEGER DEFAULT 0)
                ''')

        self.connection.commit()

    def add_category(self, category):
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
                self.add_category(item)
            elif category[0][3] == 1:
                self.lock_category(category[0][1])
                
        c.execute("SELECT * FROM Categories WHERE hide=0")
        db_active_categories = c.fetchall()
        for db_cat_record in db_active_categories:
            if db_cat_record[1] not in list:
                self.lock_category(db_cat_record[1])
            
    def get_recent_transactions(self, n):
        transactions = []
        c = self.cursor
        c.execute('SELECT * FROM Transactions ORDER BY transaction_id DESC LIMIT ?;',(n,))
        fetched = c.fetchall()
        
        for f in fetched:
            transactions.append(
                Transaction(f[1], f[2], f[3], 
                            datetime.strptime(f[4].split()[0], '%Y-%m-%d'), 
                            f[5])
            )
        return transactions
        

    def get_categories(self):
        c = self.cursor
        c.execute("SELECT * FROM Categories WHERE hide=0")
        category_list = c.fetchall()
        list = []
        for i in category_list:
            list.append(i[1])

        return list

    def add_transaction(self, t: Transaction):
        # ensure category exists
        self.update_categories((t.category,))

        c = self.cursor
        c.execute("INSERT INTO Transactions(sign,sum,category,date,note) VALUES (?,?,?,?,?)",
                  (t.sign, t.sum, t.category, t.date, t.note))
        c.execute("SELECT * FROM Categories WHERE name=?", (t.category,))
        cur_cat_freq = c.fetchall()
        c.execute("UPDATE Categories SET frequency=? WHERE name=?", (cur_cat_freq[0][2] + 1, t.category))
        self.connection.commit()

    def clear_table(self, table):
        c = self.cursor
        c.execute("DELETE FROM " + table)
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
        c.execute('DELETE FROM Categories WHERE name=?', (name,))
        self.connection.commit()
        
    def lock_category(self, name):
        c = self.cursor
        c.execute("SELECT * FROM Categories WHERE name=?", (name,))
        cur_cat = c.fetchall()
        c.execute('UPDATE Categories SET hide=? WHERE name=?', (1 - cur_cat[0][3], name))
        self.connection.commit()

    def transaction_list_to_frame(self):
        return pd.read_sql('SELECT * FROM Transactions', self.connection)


if __name__ == "__main__":
    d = Database()
    # d.clear_tables()
    # d.update_categories(['groceries','restaurants','presents', 'salary', 'home', 'beauty', 'investments'])
    # d.connection.commit()
    # d.cursor.execute('UPDATE Categories SET frequency=2 WHERE name="alcohol"')
    # d.cursor.execute('UPDATE Categories SET hide=0')
    #d.cursor.execute('UPDATE Transactions SET note="" WHERE transaction_id=305')
    # d.cursor.execute('UPDATE Transactions SET sum=38.3 WHERE transaction_id=328')
    # d.cursor.execute('ALTER TABLE Categories ADD hide INTEGER DEFAULT 0;')
    # d.cursor.execute('DELETE FROM Categories WHERE category_id>=45')
    # d.cursor.execute('DELETE FROM Transactions WHERE transaction_id>=316')
    # d.cursor.execute('SELECT * FROM Transactions WHERE transaction_id>=316')
    # d.connection.commit()
    # print(d.transaction_list_to_frame())
    print(d.transaction_list_to_frame())
