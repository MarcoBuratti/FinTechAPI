import plotly.express as px
from requests import get
from pandas import DataFrame
import plotly.io as pio
import plotly
import json

def dcf(ticker):
    balance_sheet = get('https://financialmodelingprep.com/api/v3/balance-sheet-statement/' + ticker + '?limit=120&apikey=c02b588f1788d81805c7d379c213079e').json()

    assets_liab = []
    assets_liab.append([balance_sheet[0]['totalCurrentAssets'], 'Current Assets'])
    assets_liab.append([balance_sheet[0]['totalCurrentLiabilities'], 'Current Liabilities'])
    assets_liab.append([balance_sheet[0]['totalAssets']- balance_sheet[0]['totalCurrentAssets'], 'Long term Assets'])
    assets_liab.append([balance_sheet[0]['totalLiabilities']- balance_sheet[0]['totalCurrentLiabilities'], 'Long term Liabilities'])
    assets_liab = DataFrame(assets_liab, columns = ['Value', 'Data'])

    barchart = px.bar(
        data_frame=assets_liab,
        x="Data",
        y="Value",
        color="Data",               # differentiate color of marks
        opacity=0.9,                  # set opacity of markers (from 0 to 1)
        orientation="v",              # 'v','h': orientation of the marks
        barmode='relative',           # in 'overlay' mode, bars are top of one another.


        labels={"Value":"Value in $",
        "Data":"Data"},           # map the labels of the figure
        title='Financial Health', # figure title
        width=500,                   # figure width in pixels
        height=400,                   # figure height in pixels
        template='gridon',            # 'ggplot2', 'seaborn', 'simple_white', 'plotly',
    )

    return json.dumps(barchart, cls=plotly.utils.PlotlyJSONEncoder)

