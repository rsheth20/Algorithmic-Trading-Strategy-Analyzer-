# Import necessary packages
import yfinance as yf           #pull stock prices
import pandas as pd             #data handling
pd.options.display.max_columns = 15
import numpy as np              #calculations
import ta                       #calculate technical indicatora
import matplotlib.pyplot as plt #visualize trading strategy

# Pull price data beginning from 2019
price_data = yf.download('AAPL', start='2019-01-01')

# Add column for calculate 20 day average
price_data['twenty_day_avg'] = price_data.Close.rolling(20).mean()
# Add standard deviation column 
price_data['dev'] = price_data.Close.rolling(20).std()
# Add upper bollinger band column
price_data['upper_bb'] = price_data.twenty_day_avg + (2 * price_data.dev)
# Add lower bollinger band column
price_data['lower_bb'] = price_data.twenty_day_avg - (2 * price_data.dev)
# Add RSI column
price_data['rsi'] = ta.momentum.rsi(price_data.Close, window=6)

# Define conditions for RSI, close, and bollinger bands
conditions = [(price_data.rsi < 30) & (price_data.Close < price_data.lower_bb), #Buying condition
              (price_data.rsi > 70) & (price_data.Close > price_data.upper_bb)] #Selling condition

# Define Buy and Sell choices
choices = ['Buy', 'Sell']

# Add signal column and pass conditions and choices
price_data['signal'] = np.select(conditions, choices)

# Get rid of NaN's
price_data.dropna(inplace=True)

# Shift signal column by 1 row to make the buy price the next day's open
price_data.signal = price_data.signal.shift()

# Add shifted Close column
price_data['shifted_Close'] = price_data.Close.shift()

# Loop through
position = False
buy_dates, sell_dates = [], []
buy_prices, sell_prices = [], []

for index, row in price_data.iterrows():
    if not position and row['signal'] == 'Buy':
        buy_dates.append(index)
        buy_prices.append(row.Open)
        position = True

    if position:
        if row['signal'] == 'Sell' or row.shifted_Close < 0.90 * buy_prices[-1]:   #Set stop loss
            sell_dates.append(index)
            sell_prices.append(row.Open)
            position = False
        
# Show price data        
print(price_data)

# Calculate and show total profit
profits = (pd.Series([(sell - buy) / buy for sell,buy in zip(sell_prices, buy_prices)]) + 1).prod() - 1
print(profits*100,end='%')

# Visualize the data
plt.figure(figsize=(10,5))        
plt.plot(price_data.Close)
plt.scatter(price_data.loc[buy_dates].index, price_data.loc[buy_dates].Close, marker = '^', c='g')
plt.scatter(price_data.loc[sell_dates].index, price_data.loc[sell_dates].Close, marker = 'v', c='r')
plt.show()
