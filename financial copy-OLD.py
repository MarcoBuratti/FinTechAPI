import pandas as pd     #(version 1.0.0)
import plotly           #(version 4.5.0)
import plotly.express as px
import plotly.graph_objects as go
import dash             #(version 1.8.0)
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from requests import get
import html5lib
from pandas import DataFrame
import dash_bootstrap_components as dbc


ticker = 'AMZN'
#r = get('https://financialmodelingprep.com/api/v3/' + document + '/' + ticker + '?limit=120&apikey=demo')

# Annual data
income_statement = get('https://financialmodelingprep.com/api/v3/income-statement/' + ticker + '?limit=120&apikey=c02b588f1788d81805c7d379c213079e').json()
balance_sheet = get('https://financialmodelingprep.com/api/v3/balance-sheet-statement/' + ticker + '?limit=120&apikey=c02b588f1788d81805c7d379c213079e').json()
ratios = get('https://financialmodelingprep.com/api/v3/ratios/' + ticker + '?limit=40&apikey=c02b588f1788d81805c7d379c213079e').json()
cash_flow = get('https://financialmodelingprep.com/api/v3/cash-flow-statement/' + ticker + '?limit=120&apikey=c02b588f1788d81805c7d379c213079e').json()
profile = get('https://financialmodelingprep.com/api/v3/profile/' + ticker + '?apikey=c02b588f1788d81805c7d379c213079e').json()


# list of all the FCFE, that are levered cash flows, so you have to use beta LEVERED, so the beta
FCFE = []
for i in range(min(len(cash_flow),len(income_statement),len(balance_sheet))):
    data = [cash_flow[i]['date'], (income_statement[i]['netIncome']+cash_flow[i]['depreciationAndAmortization']
    -cash_flow[i]['capitalExpenditure']-cash_flow[i]['changeInWorkingCapital']+cash_flow[i]['debtRepayment']), 'FCFE']
    FCFE.append(data)


# reverse FCFE

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
netIncome_ann


FCFE_df = DataFrame(FCFE[::-1], columns = ['Date', 'Value', 'Data'])

df = pd.concat([dataframe_revenue, netIncome_ann, FCFE_df])

assets_liab = []
assets_liab.append([balance_sheet[0]['totalCurrentAssets'], 'Current Assets'])
assets_liab.append([balance_sheet[0]['totalCurrentLiabilities'], 'Current Liabilities'])
assets_liab.append([balance_sheet[0]['totalAssets']- balance_sheet[0]['totalCurrentAssets'], 'Long term Assets'])
assets_liab.append([balance_sheet[0]['totalLiabilities']- balance_sheet[0]['totalCurrentLiabilities'], 'Long term Liabilities'])
assets_liab = DataFrame(assets_liab, columns = ['Value', 'Data'])


# https://www.bootstrapcdn.com/bootswatch/
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.GRID],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )


# Layout section: Bootstrap (https://hackerthemes.com/bootstrap-cheatsheet/)
# ************************************************************************
app.layout = dbc.Container([

    dbc.Row([
        dbc.Col([html.H1(profile[0]['companyName'] + " financial data",
                        className='text-dark text-dark mb-4')],
                        width={'size':8, 'offset':4, 'order':1}),            
    ], align="start", no_gutters=True, justify='center'), 

    dbc.Row([
        dbc.Col(html.Div('ciao come stai?',
                        className='media text-dark mb-4'),
                        width=12),    
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Dropdown(id='my-dpdn2', multi=True, value=['revenue','netIncome', 'FCFE'],
                         options=[{'label':x, 'value':x}
                                  for x in df['Data'].unique()],
                         ),      
        ], width={'size':5, 'offset':0, 'order':1},
           #xs=12, sm=12, md=12, lg=5, xl=5
        ),
    ],align="start", no_gutters=True, justify='center'),  # Horizontal:start,center,end,between,around

    dbc.Row([
        dbc.Col([
            dcc.Graph(id='line-fig2', figure={})
        ], width={'size':8, 'offset':0, 'order':1},
           #xs=12, sm=12, md=12, lg=5, xl=5
        ),
    ], align="start", no_gutters=True, justify='center'),

    dbc.Row([
        dbc.Col([
            dcc.Graph(figure = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = ratios[0]['priceEarningsRatio'],
            title = {'text': "P/E Ratio"},
            domain = {'x': [0, 1], 'y': [0, 1]}
            ))),
        ]),

        dbc.Col([
            dcc.Graph(figure = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = ratios[0]['returnOnEquity'],
            delta = {'reference': 160},
            title = {'text': "Return On Equity"},
            domain = {'x': [0, 1], 'y': [0, 1]}
            ))),
        ]),

        dbc.Col([
            dcc.Graph(figure = go.Figure(go.Indicator(
                mode = "number+delta",
                value = ratios[0]['priceToBookRatio'],
                number = {'prefix': ""},
                title = {'text': "P/B Ratio"},
                delta = {'position': "top", 'reference': 320},
                domain = {'x': [0.05, 0.5], 'y': [0.15, 0.35]}))),
        ]),
        
    ], no_gutters=True, justify='center'), 

    dbc.Row([         
        dbc.Col(
            html.H1("Financial Health",
                   className='text-center text-dark mb-4'), width=12),  
    ], align="start", no_gutters=True, justify='center'),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id='my-hist2', figure= px.bar(
                data_frame=assets_liab,
                x="Data",
                y="Value",
                color="Data",               # differentiate color of marks
                opacity=0.9,                  # set opacity of markers (from 0 to 1)
                orientation="v",              # 'v','h': orientation of the marks
                barmode='relative',
                labels={"Value":"Value in $",
                "Data":"Data"},           # map the labels of the figure
                title='', # figure title
                width=1000,                   # figure width in pixels
                height=515,                   # figure height in pixels
                template='gridon', 
            )),
        ], width={'size':0, 'offset':1})
           #xs=12, sm=12, md=12, lg=5, xl=5
    ], align="start", no_gutters=True, justify='center'),
], fluid=True)


# Callback section: connecting the components
# ************************************************************************
# Line chart - Single
""" @app.callback(
    Output('line-fig2', 'figure'),
    Input('my-dpdn2','value')
)
def update_graph(stock_slctd):
    dff = df[df['Symbols']==stock_slctd]
    figln = px.line(dff, x='Date', y='Value')
    return figln """


# Line chart - multiple
@app.callback(
    Output('line-fig2', 'figure'),
    Input('my-dpdn2', 'value')
)
def update_graph(stock_slctd):
    dff = df[df['Data'].isin(stock_slctd)]
    figln2 = px.line(dff, x='Date', y='Value', color='Data')
    return figln2


""" # Histogram
@app.callback(
    Output('my-hist', 'figure'),
    Input('my-checklist', 'value')
)
def update_graph(stock_slctd):
    dff = assets_liab[assets_liab['Data']==stock_slctd]
    fighist = px.histogram(dff, x='Data', y='Value')
    return fighist
 """

if __name__=='__main__':
    app.run_server(port=8000)
