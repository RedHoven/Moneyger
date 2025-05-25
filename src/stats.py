from datetime import datetime, timedelta
from turtle import back

from database import Database
from collections import defaultdict

class Statistics:
    def __init__(self, db) -> None:
        self.db = db
        self.records = self.db.transaction_list_to_frame()
        self.records['month'] = self.records['date'].str.split("-").apply(lambda x: x[0]+'-'+x[1])
        
        now = datetime.now()
        # now = datetime(2023, 10, 1)  # For testing purposes, set a fixed date
        self.current_month:  str = now.strftime("%Y-%m")
        self.previous_month: str = self.get_month(backdrop=1)
        
    
    def get_month(self, backdrop=0) -> str:
        year, month = self.current_month.split('-') 
        month = int(month) - backdrop
        
        if month < 1:
            year = str(int(year) - 1)
            month += 12
            
        return f'{year}-{month:02}'
        
    def get_month_stats(self, backdrop=0):
        lm_transactions = self.records[self.records['month'] == self.get_month(backdrop=backdrop)]
        data = defaultdict()
        
        # total
        total_spent = lm_transactions[lm_transactions['sign']=='-']['sum'].sum().round(2)
        total_earned = lm_transactions[lm_transactions['sign']=='+']['sum'].sum().round(2)
        total_profit = total_earned - total_spent
        
        data['total_spent'] = total_spent
        data['total_earned'] = total_earned
        data['total_profit'] = total_profit
        
        # total per category
        total_per_category = lm_transactions[lm_transactions.sign == '-'].groupby('category')['sum'].sum().sort_values(ascending=False)
        top_5_spendings = total_per_category.iloc[:5]
        frequency_per_category = lm_transactions.groupby('category')['category'].count().sort_values(ascending=False)
        top_5_frequent = frequency_per_category.iloc[:5]
        
        data["top_spendings"] = top_5_spendings.to_dict()
        data["top_frequent"] = top_5_frequent.to_dict()
        
        return data
    
    def get_summary(self):
        data = defaultdict()
        months = [self.get_month(x) for x in range(1,7)]
        
        trs = self.records[self.records['month'].isin(months)]
        data['avg_spendings_per_month'] = trs[trs['sign']=='-'].groupby('month')['sum'].sum().mean()
        data['spendings_per_month'] = trs[trs['sign']=='-'].groupby('month')['sum'].sum().to_dict()
        total_per_category = trs[trs.sign == '-'].groupby(['category','month'])['sum'].sum().to_frame()
        total_per_category.reset_index(inplace=True)
        # print(total_per_category)
        total_per_category = total_per_category.groupby('category')['sum'].sum().sort_values(ascending=False)
        data['category_per_month'] = total_per_category.iloc[:5].divide(6).to_dict()
        return data
        
        
    
if __name__ == '__main__':
    db = Database()
    s = Statistics(db)
    print(s.previous_month)
    print(s.get_summary())