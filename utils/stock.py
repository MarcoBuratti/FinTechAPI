from pandas_datareader import data as wb
import pandas as pd
import numpy as np
import time
from yahoofinancials import YahooFinancials

from utils.Stock_Functions import * 

class Stock:

    def __init__(self):
        self.mydata = None
        self.tickers = None
        self.sp500 = None
        self.yr_10 = None

    
    def initData(self, tickers, data1, data2):
        #self.tickers = ['ACN', 'TSLA', 'EZJ', 'BLK','IBM','VGT']
        #self.weights = np.array([1/6, 1/6, 1/6, 1/6, 1/6, 1/6])
        self.tickers = tickers
        self.mydata = portfolio(self.tickers, data1, data2)
        self.yr_10 = SP500()

    def getMydata(self):
        return self.mydata
    
    def getTickers(self):
        return self.tickers

    def getSP500(self):
        return self.sp500

    def getYR10(self):
        return self.yr_10

    
    #Markowitz Portfolio Optimization
    def markovitz(self):
        covRetLog = pfCov(self.mydata)
        num_assets = len(self.tickers)
        appendPfRet = returns(self.mydata).mean() * 250

        pf_returns= []
        pf_vol= []
        weig_list = []
        sharpe_list = []
        
        #generate a for loop which gives back 5000 pf weights
        #w /= sum.(w) is equivalent to w = w / sum.(w)->w1/(w1+w2) + w2/(w1+w2..) + wn/(sum.wn)=1
        for x in range(5000):
            weights_m = np.random.random( num_assets )
            weights_m /= np.sum( weights_m )
            weig_list.append( weights_m )
            singleReturn = np.sum( np.dot(weights_m, appendPfRet) )
            singleVol = np.sqrt(np.dot( weights_m.T, np.dot( covRetLog, weights_m )))
            pf_returns.append( singleReturn )
            pf_vol.append( singleVol )
            sharpe_list.append( (singleReturn - self.yr_10) / singleVol )
        
        weig_list = [np.round(num, 4) for num in weig_list]
        pf_returns = np.array(pf_returns)
        pf_vol = np.array(pf_vol)

        #create a dataframe containings three features
        portfolios = pd.DataFrame({'Return': pf_returns, 'Volatility': pf_vol, 'weig_list': weig_list, 'sharpe': sharpe_list})
        
        # Find our 3 best porfolios
        maxReturnPf = portfolios['Return'].argmax()
        minVolatilityPf = portfolios['Volatility'].argmin()
        sharpeMax = portfolios['sharpe'].argmax()
        pfpuntoMaxRet = portfolios.iloc[maxReturnPf]
        pfpuntoMinVol  = portfolios.iloc[minVolatilityPf]
        pfpuntoSharpe = portfolios.iloc[sharpeMax]
        #plot efficient frontier 
        fig = stockMarkovitz(portfolios, pfpuntoMaxRet, pfpuntoMinVol, pfpuntoSharpe,  self.getYR10(), self.getTickers())
        return fig
        #return  pfpuntoMaxRet, pfpuntoMinVol, pfpuntoSharpe, self.tickers
    

    def logRet(self, data1, data2):
        mydata = pd.DataFrame()
        mydata = wb.DataReader('AAPL',data_source='yahoo', start=data1, end=data2)['Close']
        dateStr = [str(mydata.keys()[i+1])[:-9] for i in range(len(mydata)-1)]
        vettoreDate = []
        vettorePrezzi = []
        vettoreTicker = []
        tick = self.getTickers()
        for t in tick:
            dRet = dailyReturn(portfolio(t, data1, data2))
            for i in range(len(dateStr)):
                vettoreDate.append(dateStr[i])
                vettorePrezzi.append(dRet[i])
                vettoreTicker.append(t)
        d = { 'Date': vettoreDate, 'Ticker': vettoreTicker, 'Price': vettorePrezzi}
        df = pd.DataFrame(data=d)
        return plotLogRet(df)