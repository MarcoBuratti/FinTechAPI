import pandas as pd     #(version 1.0.0)
import plotly           #(version 4.5.0)
import plotly.express as px
import plotly.graph_objects as go
from requests import get
from pandas import DataFrame
import json

def get_data(ticker):
    ratios = get('https://financialmodelingprep.com/api/v3/ratios/' + ticker + '?limit=40&apikey=c02b588f1788d81805c7d379c213079e').json()
    return ratios 

def getDescription(ticker):
    profile = get('https://financialmodelingprep.com/api/v3/profile/' + ticker + '?apikey=c02b588f1788d81805c7d379c213079e').json()
    return profile[0]['description']

def get_exchange(ticker):
    profile = get('https://financialmodelingprep.com/api/v3/profile/' + ticker + '?apikey=c02b588f1788d81805c7d379c213079e').json()
    return profile[0]['exchangeShortName']

def get_dataframe(ticker):
    income_statement = get('https://financialmodelingprep.com/api/v3/income-statement/' + ticker + '?limit=120&apikey=c02b588f1788d81805c7d379c213079e').json()
    balance_sheet = get('https://financialmodelingprep.com/api/v3/balance-sheet-statement/' + ticker + '?limit=120&apikey=c02b588f1788d81805c7d379c213079e').json()
    cash_flow = get('https://financialmodelingprep.com/api/v3/cash-flow-statement/' + ticker + '?limit=120&apikey=c02b588f1788d81805c7d379c213079e').json()

    FCFE = []
    for i in range(min(len(cash_flow),len(income_statement),len(balance_sheet))):
        data = [cash_flow[i]['date'], (income_statement[i]['netIncome']+cash_flow[i]['depreciationAndAmortization']
        -cash_flow[i]['capitalExpenditure']-cash_flow[i]['changeInWorkingCapital']+cash_flow[i]['debtRepayment']), 'FCFE']
        FCFE.append(data)

    FCFE_rev = FCFE[::-1]
    revenue_ann = []
    netIncome_ann = []

    for i in range(len(income_statement)):
        var = [income_statement[i]['date'], income_statement[i]['revenue'], 'revenue']
        var_income = [income_statement[i]['date'], income_statement[i]['netIncome'], 'netIncome']
        revenue_ann.append(var)
        netIncome_ann.append(var_income)
    netIncome_ann = netIncome_ann[::-1]

    revenue_ann_rev = []
    for j in range(1,len(revenue_ann)+1):
        revenue_ann_rev.append(revenue_ann[-j])    

    # creating pandas dataframe for Holt Winters model
    dataframe_revenue = DataFrame(revenue_ann_rev, columns=['Date','Value', 'Data'])

    # computing percentage of FCFE respect to revenues  
    perc_of_revenues = []
    for i in range(min(len(cash_flow),len(income_statement),len(balance_sheet))):
        rapporto = FCFE[i][1]/income_statement[i]['revenue']
        FCFE_perc = [income_statement[i]['date'], rapporto]
        perc_of_revenues.append(FCFE_perc)

    net_income = [[revenue_ann_rev[i][0][:4], '' , 'netIncome' ] for i in range(len(revenue_ann_rev))]
    netIncome_ann = DataFrame(netIncome_ann, columns = ['Date', 'Value', 'Data'])

    FCFE_df = DataFrame(FCFE[::-1], columns = ['Date', 'Value', 'Data'])
    df = pd.concat([dataframe_revenue, netIncome_ann, FCFE_df])

    assets_liab = []
    assets_liab.append([balance_sheet[0]['totalCurrentAssets'], 'Current Assets'])
    assets_liab.append([balance_sheet[0]['totalCurrentLiabilities'], 'Current Liabilities'])
    assets_liab.append([balance_sheet[0]['totalAssets']- balance_sheet[0]['totalCurrentAssets'], 'Long term Assets'])
    assets_liab.append([balance_sheet[0]['totalLiabilities']- balance_sheet[0]['totalCurrentLiabilities'], 'Long term Liabilities'])
    assets_liab = DataFrame(assets_liab, columns = ['Value', 'Data'])

    return df, assets_liab 

def draw_lines(ticker):
    df, assets_liab = get_dataframe(ticker)
    figure= px.line(df, x=df['Date'], y=df['Value'], color=df['Data'],
                width=1000,                   # figure width in pixels
                height=500, 
            )
    return json.dumps(figure, cls=plotly.utils.PlotlyJSONEncoder) 

def draw_bars(ticker):
    df, assets_liab = get_dataframe(ticker)
    fig = px.bar(
                data_frame=assets_liab.iloc[:2],
                x="Data",
                y="Value",
                color="Data",               # differentiate color of marks
                opacity=0.9,                  # set opacity of markers (from 0 to 1)
                orientation="v",              # 'v','h': orientation of the marks
                barmode='relative',
                labels={"Value":"Value in $",
                "Data":"Short Term"},           # map the labels of the figure
                title='', # figure title
                width=450,                   # figure width in pixels
                height=400,                   # figure height in pixels
                template='gridon')
    fig2 = px.bar(
                data_frame=assets_liab.iloc[2:],
                x="Data",
                y="Value",
                color="Data",               # differentiate color of marks
                opacity=0.9,                  # set opacity of markers (from 0 to 1)
                orientation="v",              # 'v','h': orientation of the marks
                barmode='relative',
                labels={"Value":"",
                "Data":"Long Term"},           # map the labels of the figure
                title='', # figure title
                width=450,                   # figure width in pixels
                height=400,                   # figure height in pixels
                template='gridon', 
            ) 
    finHealth1 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    finHealth2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
    finHealth = []
    o = {
    'ds': 'financial1',
    'fig': finHealth1
    }
    finHealth.append(o)
    o = {
        'ds': 'financial2',
        'fig': finHealth2
    }
    finHealth.append(o)
    return finHealth

def draw_indicators(ticker):
    ratios = get_data(ticker)
    ind1 = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = ratios[0]['priceEarningsRatio'],
            delta = {'reference': 50},
            title = {'text': "P/E Ratio"},
            domain = {'x': [0, 1], 'y': [0, 1]}
            ),
            layout=go.Layout(height=300, width=300)
        )
    fig1 = json.dumps(ind1, cls=plotly.utils.PlotlyJSONEncoder)
    ind2 = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = ratios[0]['returnOnEquity'],
            delta = {'reference': 50},
            title = {'text': "Return On Equity"},
            domain = {'x': [0, 1], 'y': [0, 1]}
            ),
            layout=go.Layout(height=300, width=300)
        )
    fig2 = json.dumps(ind2, cls=plotly.utils.PlotlyJSONEncoder)
    ind3 = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = ratios[0]['priceToBookRatio'],
            number = {'prefix': ""},
            title = {'text': "P/B Ratio"},
            delta = {'reference': 50},
            domain = {'x': [0, 1], 'y': [0, 1]}
            ),
            layout=go.Layout(height=300, width=300)
        )
    fig3 = json.dumps(ind3, cls=plotly.utils.PlotlyJSONEncoder)
    indicator = []
    o = {
    'ds': 'indicator1',
    'fig': fig1
    }
    indicator.append(o)
    o = {
    'ds': 'indicator2',
    'fig': fig2
    }
    indicator.append(o)
    o = {
    'ds': 'indicator3',
    'fig': fig3
    }
    indicator.append(o)
    return indicator
