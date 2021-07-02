from datetime import date
import yfinance as yf
import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
from btcusd_strategy_model import Model

class Strategy:
    def __init__(self, ticker, start_date, end_date, interval, model):
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.interval = interval
        self.strategydb = model

    def get_data(self):
        data = yf.download(tickers = self.ticker, start=self.start_date, end=self.end_date, interval = self.interval, auto_adjust = True)
        data = data.fillna(method='ffill')
        data.index = pd.to_datetime(data.index, format = '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
        data['SMA_14'] = data.Close.rolling(14).mean()
        data['SMA_36'] = data.Close.rolling(36).mean()
        # Если 0, то SMA_14 ниже SMA_36, 
        # если 1, то SMA(14) выше SMA(36)
        data['Direction'] = 0.0
        data['Direction'] = np.where(data['SMA_14'] > data['SMA_36'], 1.0, 0.0)
        # По столбцу Position. Если 1, то купить на фиксированный лот, 
        # если -1, то продать на фиксированный лот,
        # если 0, то пропустить 
        data['Position'] = data['Direction'].diff()
        data.fillna(method='bfill', inplace=True)
        return data

    @staticmethod
    def get_position_quantity(self, current_position):
        quantity = current_position * 0.1
        return quantity
    
    @staticmethod
    def make_deal(self, date, order_side, order_quantity, quantity, price, pos_id):
        self.strategydb.insert_rows(date, order_side, order_quantity, quantity, price, pos_id)

    def write_deals_to_db(self, data):
        current_position_id = 0
        # 0 - закрыта, 1 - long, -1 - short
        current_position = 0
        position_quantity = 0
        buy_order = 'BUY'
        sell_order = 'SELL'
        quantity_to_buy = 0.1
        quantity_to_sell = -0.1
        for index, row in data.iterrows():
            if current_position == 0:
                if row.Position == 1:
                    current_position_id +=1
                    current_position +=1
                    position_quantity = self.get_position_quantity(self, current_position)
                    self.make_deal(self, index, buy_order, quantity_to_buy, position_quantity, row.Close, current_position_id)
                elif row.Position == -1:
                    current_position_id +=1
                    current_position -=1
                    position_quantity = self.get_position_quantity(self, current_position)
                    self.make_deal(self, index, sell_order, quantity_to_sell, position_quantity, row.Close, current_position_id)          
            elif current_position == 1 and row.Position == -1:
                current_position -=1
                position_quantity = self.get_position_quantity(self, current_position)
                self.make_deal(self, index, sell_order, quantity_to_sell, position_quantity, row.Close, current_position_id)    
                current_position_id +=1
                current_position -=1
                position_quantity = self.get_position_quantity(self, current_position)
                self.make_deal(self, index, sell_order, quantity_to_sell, position_quantity, row.Close, current_position_id)   
            elif current_position == -1 and row.Position == 1:
                current_position +=1
                position_quantity = self.get_position_quantity(self, current_position)
                self.make_deal(self, index, buy_order, quantity_to_buy, position_quantity, row.Close, current_position_id) 
                current_position_id +=1
                current_position +=1
                position_quantity = self.get_position_quantity(self, current_position)
                self.make_deal(self, index, buy_order, quantity_to_buy, position_quantity, row.Close, current_position_id) 
        print('Сделки записаны в базу данных')

    def set_start_deposit(self, data):
        deposit = data.iloc[0].Close
        print(deposit)
        return deposit

    def get_strategy_results(self):
        positions_results = self.strategydb.get_positions_result()
        positions_results = pd.DataFrame(data = positions_results, columns = ['position_closed_date', 'pos_id', 'pos_profit_lose'])
        positions_results.set_index('pos_id', inplace=True)
        avg_entry_price = self.strategydb.get_avg_entry_price()
        avg_exit_price = self.strategydb.get_avg_exit_price()
        bot_profit_lose = self.strategydb.get_bot_profit_lose()
        strategy_results = {
                            'positions_results':positions_results, 
                            'avg_entry_price': avg_entry_price[0], 
                            'avg_exit_price':avg_exit_price[0], 
                            'bot_profit_lose':bot_profit_lose[0]
                            }
        return strategy_results

    @staticmethod
    def get_max_lose_seria(self, df):
        m = df['pos_profit_lose'].lt(0)
        ser = (m != m.shift())[m].cumsum()
        grouped = ser.groupby(ser).count()
        max_lose_seria = grouped.max()
        return max_lose_seria
        
    def vizualize_strategy_parameters(self, start_deposit, strategy_results):
        positions_df = strategy_results['positions_results']
        positions_df['cumsum_pnl'] = positions_df['pos_profit_lose'].cumsum()
        positions_df['deposit_change'] = positions_df['cumsum_pnl'].apply(lambda x: start_deposit + x)
        positions_df['deposit_change_percent'] = positions_df['deposit_change'].apply(lambda x: (x - start_deposit) / start_deposit * 100)

        start_deposit = start_deposit
        max_drawdown = positions_df['deposit_change_percent'].min()
        amount_of_deals = len(positions_df.index)
        amount_of_posit_deals = sum(n >= 0 for n in positions_df['pos_profit_lose']) / amount_of_deals * 100
        amount_of_negat_deals = sum(n < 0 for n in positions_df['pos_profit_lose']) / amount_of_deals * 100 
        avg_profit_deal = positions_df[positions_df.pos_profit_lose > 0]['pos_profit_lose'].mean()
        avg_lose_deal = positions_df[positions_df.pos_profit_lose < 0]['pos_profit_lose'].mean()
        max_lose_seria = self.get_max_lose_seria(self, positions_df)
        recovery_factor = strategy_results['bot_profit_lose'] / (start_deposit - positions_df['deposit_change'].min())
        avg_entry_price = strategy_results['avg_entry_price']
        avg_exit_price = strategy_results['avg_exit_price']
        bot_profit_lose = strategy_results['bot_profit_lose']

        print(start_deposit)
        print(positions_df)
        print('max_drawdown', max_drawdown)
        print('amount_of_deals', amount_of_deals)
        print('amount_of_posit_deals', amount_of_posit_deals)
        print('amount_of_negat_deals', amount_of_negat_deals)
        print('avg_profit_deal', avg_profit_deal)
        print('avg_lose_deal', avg_lose_deal)
        print('max_lose_seria', max_lose_seria)
        print('recovery_factor', recovery_factor)
        print('avg_entry_price', avg_entry_price)
        print('avg_exit_price', avg_exit_price)
        print('bot_profit_lose', bot_profit_lose)

        x1 = np.linspace(0.0, 433.0, num=433)
        x2 = np.linspace(0.0, 433.0, num=433)
        
        y1 = positions_df['deposit_change_percent']
        y2 = positions_df['cumsum_pnl']
        
        fig, (ax1, ax2) = plt.subplots(2, 1)
        fig.suptitle('Графики доходности и просадки')
        
        ax1.plot(x1, y1, 'o-')
        ax1.set_ylabel('Доходность, в %')
        
        ax2.plot(x2, y2, '.-')
        ax2.set_xlabel('time (s)')
        ax2.set_ylabel('Просадка, USD')
        
        plt.show()

if __name__ == "__main__":
    model = Model()
    ticker = 'BTC-USD'
    start_date = '2020-01-01'
    interval = '1h'
    end_date = date.today().strftime('%Y-%m-%d')
    strategy = Strategy(ticker, start_date, end_date, interval, model)
    data = strategy.get_data()
    strategy.write_deals_to_db(data)
    start_deposit = strategy.set_start_deposit(data)
    strategy_results = strategy.get_strategy_results()
    strategy.vizualize_strategy_parameters(start_deposit, strategy_results)
    
    

    