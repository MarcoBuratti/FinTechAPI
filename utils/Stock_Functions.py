from pandas_datareader import data as wb
from yahoofinancials import YahooFinancials
import pandas as pd
import numpy as np

import plotly.graph_objects as go
import plotly.express as px
import plotly
import json

# Select data from database
def portfolio(t, data1, data2):
    print('Downloading data....')
    mydata = pd.DataFrame()
    mydata[t]= wb.DataReader(t,data_source='yahoo', start=data1, end=data2)['Adj Close']
    return mydata    
    
def SP500():
    yahoo_financials = YahooFinancials('^TNX')
    yr_10 = yahoo_financials.get_current_price()/100  
    return yr_10
      
#calculate a portfolio annual return
def pf_return(mydata):
    returns = (mydata/ mydata.shift(1)) -1
    annual_returns= returns.mean() * 250
    return annual_returns

#ritorna rendimenti giornalieri
def returns(mydata):
    return np.log((mydata/ mydata.shift(1)))
    
    
# Ritorna portfolio pesato
def weigthedReturn(annual_returns, weights):
    return round(np.dot(annual_returns, weights), 4)*100
    
# Ritorna il rischio del portafoglio    
def pfRisk(annual_returns, tickers):
    return annual_returns[tickers].std() 


#calcola cov portafoglio
def pfCov(mydata):
    return returns(mydata).cov() * 250


#calcola corr portafoglio
def pfCorr(mydata):
    return returns(mydata).corr() 

# Plot trend
"""
def recap(x, y):
    plt.plot(x, y)
    plt.annotate( str( int(y[-1]) ), (250, y[-1]) )
    plt.ylabel('Equity Line')
    plt.xlabel('Days')
    plt.savefig('./img/recap.png')
    plt.close('all')

def stockRecap(mydata, tickers):
    #mydata.plot(figsize=(16,8))
    plt.plot(mydata)
    for t in tickers:
        plt.annotate( str( t ), ('2020-01-01', mydata.get(t)[0]) )
    plt.ylabel('Stock prices')
    plt.xlabel('Days')
    plt.savefig('./img/stock.png')
    plt.close('all')
"""
def stockMarkovitz(portfolios, pfpuntoMaxRet, pfpuntoMinVol, sharpeMax, riskFree, tickers):
    
    m = (sharpeMax['Return']- riskFree)/ (sharpeMax['Volatility'])
    xGreen = pfpuntoMinVol['Volatility']/1.2
    yGreen = m * (xGreen) + riskFree
    label = ''
    for i in range(len(sharpeMax['weig_list'])):
        label += tickers[i] + ': ' + str(round(sharpeMax['weig_list'][i]*100, 3)) + '%\n'
    label += 'Porftofolio return: ' + str(round( sharpeMax['Return']*100, 3)) + '%\n'
    label += 'Porftofolio risk: ' + str(round( sharpeMax['Volatility']*100, 3)) + '%\n'

    fig = px.scatter(portfolios, x="Volatility", y="Return", color='sharpe',
                      width=1000,                   # figure width in pixels
                      height=500,                   # figure height in pixels 
                     )
    fig.add_trace(
      go.Scatter(
          x=[xGreen, sharpeMax['Volatility']],
          y=[yGreen, sharpeMax['Return']],
          mode="lines",
          line=go.scatter.Line(color="green"),
          showlegend=False
        )
    )
    fig.add_trace(
      go.Scatter(
          x=[sharpeMax['Volatility'], sharpeMax['Volatility']],
          y=[sharpeMax['Return'], sharpeMax['Return']],
          marker= dict(size=15),
          text=label,
          line=go.scatter.Line(color="green"),
          showlegend=False
        )
    )
    label = ''
    for i in range(len(pfpuntoMinVol['weig_list'])):
        label += tickers[i] + ': ' + str(round(pfpuntoMinVol['weig_list'][i]*100, 3)) + '%\n'
    label += 'Porftofolio return: ' + str(round( pfpuntoMinVol['Return']*100, 3)) + '%\n'
    label += 'Porftofolio risk: ' + str(round( pfpuntoMinVol['Volatility']*100, 3)) + '%\n'
    fig.add_trace(
      go.Scatter(
          x=[pfpuntoMinVol['Volatility'], pfpuntoMinVol['Volatility']],
          y=[pfpuntoMinVol['Return'], pfpuntoMinVol['Return']],
          marker= dict(size=15),
          text=label,
          line=go.scatter.Line(color="green"),
          showlegend=False
        )
    )
    #fig.show()
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def plotLogRet(df):
    fig = px.line(df, x="Date", y="Price", color="Ticker",
              width=1000,                   # figure width in pixels
              height=500, 
              )

    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

#calculate a portfolio annual return
def dailyReturn(mydata):
    daily = (mydata/ mydata.shift(1)).mean(axis = 1) - 1
    lenght = daily.size
    new_list=[] 
    day_list=[]
    i=0
    j=0
    # Cumulated return
    for i in range(1, lenght):
        j+=daily.iloc[i]
        #aggiungi elemento j in coda alla lista
        new_list.append(j)
        i+=1
        day_list.append(i)
    l = [1 + (x * 1) for x in new_list]
    return l