import json
from utils.dcf import *
from pandas import DataFrame
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import numpy as np
import pandas as pd
from country_list import countries_for_language
from bs4 import BeautifulSoup
from requests import get
import plotly.graph_objects as go
import plotly           #(version 4.5.0)


def offLineDCF(ticker):
    path = './static/assets/DCF/'+ ticker + '/balance_sheet_quar.json'
    with open(path) as json_file:
        balance_sheet_quar = json.load(json_file)
    path = './static/assets/DCF/'+ ticker + '/balance_sheet.json'
    with open(path) as json_file:
        balance_sheet = json.load(json_file)
    path = './static/assets/DCF/'+ ticker + '/cash_flow_quar.json'
    with open(path) as json_file:
        cash_flow_quar = json.load(json_file)
    path = './static/assets/DCF/'+ ticker + '/cash_flow.json'
    with open(path) as json_file:
        cash_flow = json.load(json_file)
    path = './static/assets/DCF/'+ ticker + '/EV.json'
    with open(path) as json_file:
        EV = json.load(json_file)
    path = './static/assets/DCF/'+ ticker + '/income_statement.json'
    with open(path) as json_file:
        income_statement = json.load(json_file)
    path = './static/assets/DCF/'+ ticker + '/income_statement_quar.json'
    with open(path) as json_file:
        income_statement_quar = json.load(json_file)
    path = './static/assets/DCF/'+ ticker + '/profile.json'
    with open(path) as json_file:
        profile = json.load(json_file)
    path = './static/assets/DCF/'+ ticker + '/market_return.json'
    with open(path) as json_file:
        market_return = json.load(json_file)
        market_return = float(market_return)

        # list of all the FCFE, that are levered cash flows, so you have to use beta LEVERED, so the beta
    FCFE = []
    for i in range(min(len(cash_flow),len(income_statement),len(balance_sheet))):
        data = [cash_flow[i]['date'], (income_statement[i]['netIncome']+cash_flow[i]['depreciationAndAmortization']
        -cash_flow[i]['capitalExpenditure']-cash_flow[i]['changeInWorkingCapital']+cash_flow[i]['debtRepayment'])]
        FCFE.append(data)

    # list of all the quarterly FCFE
    FCFE_quar = []
    for i in range(min(len(balance_sheet_quar),len(income_statement_quar),len(cash_flow_quar))):
        data_quar = [balance_sheet_quar[i]['date'], (income_statement_quar[i]['netIncome']+cash_flow_quar[i]['depreciationAndAmortization']
        -cash_flow_quar[i]['capitalExpenditure']-cash_flow_quar[i]['changeInWorkingCapital']+cash_flow_quar[i]['debtRepayment'])]
        FCFE_quar.append(data_quar)


    # reversing the list of FCFE   
    FCFE_quar_rev = []
    for i in range(1, len(FCFE_quar)+1):
        FCFE_quar_rev.append(FCFE_quar[-i])

    FCFE_rev = []
    for j in range(1,len(FCFE)+1):
        FCFE_rev.append(FCFE[-j])


    revenue_quar = []
    revenue_ann = []
    for i in range(len(income_statement)):
        var = [income_statement[i]['date'], income_statement[i]['revenue']]
        revenue_ann.append(var)

    for j in range(len(income_statement_quar)):
        var1 = [income_statement_quar[j]['date'], income_statement_quar[j]['revenue']]
        revenue_quar.append(var1)

    revenue_quar_rev = []
    for i in range(1, len(revenue_quar)+1):
        revenue_quar_rev.append(revenue_quar[-i])

    revenue_ann_rev = []
    for j in range(1,len(revenue_ann)+1):
        revenue_ann_rev.append(revenue_ann[-j])    

    # creating pandas dataframe for Holt Winters model
    dataframe_revenue_quar = DataFrame(revenue_quar_rev, columns=['Date','Quarterly revenue'])
    dataframe_revenue = DataFrame(revenue_ann_rev, columns=['Date','Annual revenue'])

    # ------------------------------------ DEFINITIVE MODEL -------------------------------------------------------------
    
    # computing percentage of FCFE respect to revenues  
    perc_of_revenues = []
    for i in range(min(len(cash_flow),len(income_statement),len(balance_sheet))):
        rapporto = FCFE[i][1]/income_statement[i]['revenue']
        FCFE_perc = [income_statement[i]['date'], rapporto]
        perc_of_revenues.append(FCFE_perc)


    # past 12 years average percentage of FCFE respect to revenue
    somma = 0
    for j in range(10):
        somma += perc_of_revenues[j][1]
        average_percentage_annual = abs(somma/10)

    # making the revenue prediction from 2021 to 2027

    train_quar_2021_2027 = dataframe_revenue_quar
    hwmodel_pred = ExponentialSmoothing(train_quar_2021_2027['Quarterly revenue'],trend= 'add', seasonal= 'mul', seasonal_periods=4).fit()

    pred_test_quar_2021_2027 = hwmodel_pred.forecast(25)
    # create list of predicted dates - quarterly
    ranges = pd.date_range(revenue_ann_rev[-1][0], periods=25, freq='BQ')

    # create complete quarterly dataframe, with predictions + actual data
    s = 25
    for i in range(s):
        c = DataFrame([[str(ranges[i])[:-9], pred_test_quar_2021_2027.iloc[i]]], columns=['Date','Quarterly revenue'] )
        dataframe_revenue_quar = dataframe_revenue_quar.append(c,ignore_index=True)

    # create list of predicted dates - quarterly
    ranges_year = pd.date_range(dataframe_revenue_quar.iloc[0][0], periods=round(len(dataframe_revenue_quar)/4), freq='AS')


    #building complete annual dataframe, with predictions + actual data
    for i in range(len(ranges_year)):
        lista = [str(ranges_year[i])[:-9], '']
        revenue_ann_rev.append(lista)

    annual_complete_dataframe = []
    somma = 0
    count = 0
    for i in range(int(dataframe_revenue_quar.iloc[0]['Date'][:4]),int(dataframe_revenue_quar.iloc[-1]['Date'][:4])+1):
        for j in range(len(dataframe_revenue_quar)):
            if str(i) == dataframe_revenue_quar.iloc[j]['Date'][:4]:
                somma += dataframe_revenue_quar.iloc[j]['Quarterly revenue']
                count +=1
                if count == 4:
                    annual_complete_dataframe.append([i, somma])
                    count = 0
                    somma = 0
    annual_complete_dataframe = DataFrame(annual_complete_dataframe, columns=['Date', 'Annual revenue'])

    # plot of historical annual revenues + predicted revenues

    #annual_complete_dataframe.iloc[-6:]['Annual revenue'].plot(legend=True, label='predicted')
    #annual_complete_dataframe[:-6]['Annual revenue'].plot(legend=True, label='Train', figsize=(10,6))
    
    #############################################################################################################    

    # Get the risk-free rate table on the basis of the country of the company. The time horizon is 7 years

    countries = dict(countries_for_language('en'))
    url = 'http://www.worldgovernmentbonds.com/country/' + countries[profile[0]['country']].replace(' ','-').lower()
    tables_list = pd.io.html.read_html(url)


    for i in range(len(tables_list[4])):
        if '10 years' in str(tables_list[4].iloc[i]['ResidualMaturity']):
            RF = float(tables_list[4].iloc[i]['Yield']['Last'][:-1])/100

    url = 'https://finance.yahoo.com/quote/'+ ticker 
    tables_list = pd.io.html.read_html(url)
    beta = float(tables_list[1][1][1])

    ke = RF + beta*(market_return - RF)

    annual_predicted_revenues_2021_2026 = list(annual_complete_dataframe.iloc[-6:]['Annual revenue'])
    FCFE_2021 = [annual_predicted_revenues_2021_2026[i]*average_percentage_annual for i in range(0,len(annual_predicted_revenues_2021_2026))]
    FCFE_2021_2026 = [FCFE[0][1]]
    for i in range(len(FCFE_2021)):
        FCFE_2021_2026.append(FCFE_2021[i])


    TV = FCFE_2021_2026[6]/ke
    attualized_FCFE = []
    FCFE_att_sum = 0 
    for i in range(0,7):
        FCFE_att_sum += FCFE_2021_2026[i]/(1+ke)**i
        attualized_FCFE.append(FCFE_2021_2026[i]/(1+ke)**i)
        if i == 6:
            att_TV = TV/(1+ke)**i
    value = att_TV + FCFE_att_sum
    price = value/EV[0]['numberOfShares']   

    # DCF with analysts estimations
    page = get('https://finance.yahoo.com/quote/'+ ticker + '/analysis?p='+ ticker)
    soup = BeautifulSoup(page.text , 'html.parser')
    stima = soup.find_all('td', {'class' : 'Ta(end) Py(10px)'})
    for i in range(len(stima)):
            if 'data-reactid="427"' in str(stima[i]) and 'N/A' not in str(stima[i]) and '0.00%' not in str(stima[i]):
                estimated_growth = float(str(stima[i]).split('>')[1][:-5])/100
    FCFE_2021_2026_high = [FCFE_2021_2026[0]]
    for i in range(1,len(FCFE_2021_2026)):
        FCFE_2021_2026_high.append(FCFE_2021_2026_high[i-1]*(1+estimated_growth))

    TV = FCFE_2021_2026_high[6]/ke
    attualized_FCFE_high = []
    FCFE_att_sum_high = 0 
    for i in range(0,7):
        FCFE_att_sum_high += FCFE_2021_2026_high[i]/(1+ke)**i
        attualized_FCFE_high.append(FCFE_2021_2026[i]/(1+ke)**i)
        if i == 6:
            att_TV_high = TV/(1+ke)**i
    value_high = att_TV_high + FCFE_att_sum_high
    price_high = value_high/EV[0]['numberOfShares']  
    final_price = (price_high + price)/2

    fig = go.Figure(go.Indicator(
    mode = "gauge", value = profile[0]['price'],
    domain = {'x': [0, 1], 'y': [0, 1]},
    delta = {'reference': final_price, 'position': "top"},
    #title = {'text':"<b>DCF</b><br><span style='color: gray; font-size:0.8em'>Price in U.S. $</span>", 'font': {"size": 20}},
    gauge = {
            'shape': "bullet",
            'axis': {'range': [final_price*(1-0.7), final_price*(1+0.7)]},
            'threshold': {
                'line': {'color': "white", 'width': 0},
                'thickness': 1, 'value': profile[0]['price']},
            'bgcolor': "white",
            'steps': [
                {'range': [final_price*(1-0.7), final_price*(1-0.1)], 'color': "limegreen"},
                {'range': [final_price*(1-0.1), final_price*(1+0.1)], 'color': "gold"},
                {'range': [final_price*(1+0.1), final_price*(1+0.7)], 'color': "red"}],
            'bar': {'color': "grey"}}))
    fig.update_layout(height = 250, width = 600)

    fig = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    dcfImg = []
    comment = 'According to our DCF model, the intrinsic value of the stock ' + ticker + ' is ' + str(round(final_price, 3)) + '$'    
    o = {
        'ds': 'dcf',
        'fig': fig,
        'comment': comment
    }
    dcfImg.append(o)
    return dcfImg


def dcf(ticker):
    with open('./static/assets/DCF/TICKER_LIST/ticker_list.json') as json_file:
        data = json.load(json_file)
    if ticker in data:
        return offLineDCF(ticker)
    else:
        return onLineDCF(ticker)

