import plotly.express as px
import pandas as pd
from Stock_Functions import *
from pandas_datareader import data as wb

from yahoofinancials import YahooFinancials





tickers = ['AMZN', 'BLK','IBM','VGT', 'EZJ', 'FB', 'C', 'JPM']
weights = np.array([1/4, 1/4, 1/4, 1/4])

dataFrame = []
tick = []
d = []
p = []

mydata = pd.DataFrame()
mydata = wb.DataReader('AAPL',data_source='yahoo', start='2020-01-02', end='2020-01-31')['Close']
dateStr = [str(mydata.keys()[i+1])[:-9] for i in range(len(mydata)-1)]
for t in tickers:
    mydata = portfolio(t)
    dataset = dailyReturn(mydata)
    for i in range(len(dataset[0])):
        tick.append(t)
        p.append(dataset[1][i])

for i in range(len(tickers)):
    for j in range(len(dateStr)):
        d.append(dateStr[j])

dataFrame = {
    'ticker': tick,
    'day': d,
    'price': p
}

print(dataFrame['day'])

df = pd.DataFrame(data=dataFrame)
print(df)
fig = px.line(df, x="day", y="price", color='ticker',
        title='Financial Performance', # figure title
        width=1000,                   # figure width in pixels
        height=600,                   # figure height in pixels
    )
fig.show()

