import plotly.graph_objects as go
import numpy as np
import pandas as pd
import numpy as np
from Stock_Functions import * 

import plotly.express as px
from pandas_datareader import data as wb

tickers = ['AMZN', 'BLK','IBM','VGT']
weights = np.array([1/4, 1/4, 1/4, 1/4])
mydata = portfolio(tickers)
yr_10 = SP500()

def markovitz():
    covRetLog = pfCov(mydata)
    corrRetLog = pfCorr(mydata)
    num_assets = len(tickers)
    appendPfRet = returns(mydata).mean() * 250

    pf_returns= []
    pf_vol= []
    weig_list = []
    sharpe_list = []
    
    #generate a for loop which gives back 5000 pf weights
    #w /= sum.(w) is equivalent to w = w / sum.(w)->w1/(w1+w2) + w2/(w1+w2..) + wn/(sum.wn)=1
    for x in range(10000):
        weights_m = np.random.random( num_assets )
        weights_m /= np.sum( weights_m )
        weig_list.append( weights_m )
        singleReturn = np.sum( np.dot(weights_m, appendPfRet) )
        singleVol = np.sqrt(np.dot( weights_m.T, np.dot( covRetLog, weights_m )))
        pf_returns.append( singleReturn )
        pf_vol.append( singleVol )
        sharpe_list.append( (singleReturn - yr_10) / singleVol )
    
    weig_list = [np.round(num, 4) for num in weig_list]
    pf_returns = np.array(pf_returns)
    pf_vol = np.array(pf_vol)

    #create a dataframe containings three features
    portfolios = pd.DataFrame({'Return': pf_returns, 'Volatility': pf_vol, 'weig_list': weig_list, 'sharpe': sharpe_list})
    return pf_vol, pf_returns, sharpe_list
    # Find our 3 best porfolios
    """
    maxReturnPf = portfolios['Return'].argmax()
    minVolatilityPf = portfolios['Volatility'].argmin()
    sharpeMax = portfolios['sharpe'].argmax()
    pfpuntoMaxRet = portfolios.iloc[maxReturnPf]
    pfpuntoMinVol  = portfolios.iloc[minVolatilityPf]
    pfpuntoSharpe = portfolios.iloc[sharpeMax]
    #plot efficient frontier 
    stockMarkovitz(portfolios, pfpuntoMaxRet, pfpuntoMinVol, pfpuntoSharpe)
    
    return  pfpuntoMaxRet, pfpuntoMinVol, pfpuntoSharpe, self.tickers
    """

"""
vol, ret, shrpe = markovitz()
fig = go.Figure(data=go.Scattergl(
    x = vol,
    y = ret,
    mode='markers',
    marker=dict(
        color=shrpe,
        colorscale='Viridis',
        line_width=1
    )
))
fig.show()
"""

#logRet = np.log(mydata/mydata.shift(1))
#print(logRet)
dataFrame = []
tick = []
d = []
p = []

mydata = pd.DataFrame()
mydata = wb.DataReader('AAPL',data_source='yahoo', start='2020-01-02', end='2020-12-31')['Close']
dateStr = [str(mydata.keys()[i+1])[:-9] for i in range(len(mydata)-1)]
for t in tickers:
    mydata = portfolio(t)
    dataset = returns(mydata)
    dataset = dataset[1:]
    for i in range(len(dataset)):
        tick.append(t)
        p.append(dataset.iloc[i][0])

for i in range(len(tickers)):
    for j in range(len(dateStr)):
        d.append(dateStr[j])

dataFrame = {
    'ticker': tick,
    'day': d,
    'price': p
}
df = pd.DataFrame(data=dataFrame)
fig = px.line(df, x="day", y="price", color='ticker',
        title='Financial Performance', # figure title
        width=1000,                   # figure width in pixels
        height=600,                   # figure height in pixels
    )
fig.show()

avg = []
for t in tickers:
  x = 0.0
  for i in range(len(df)):
    if df.iloc[i]['ticker'] == t:
      x += df.iloc[i]['price']
  newAvg = {
  'ticker': t,
  'avg':  x / (len(df)/4)
  }
  avg.append(newAvg)

