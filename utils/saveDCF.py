import os
import json

def saveDCF(ticker, profile, income_statement, income_statement_quar, balance_sheet, balance_sheet_quar, EV, cash_flow, cash_flow_quar, market_return):
    # define the name of the directory to be created
    path = "./static/assets/DCF/" + ticker
    print(path)
    try:
        os.mkdir(path)
    except OSError:
        print ("Creation of the directory %s failed" % path)
    else:
        print ("Successfully created the directory %s " % path)

    path = './static/assets/DCF/'+ ticker + '/balance_sheet_quar.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(balance_sheet_quar, f, ensure_ascii=False, indent=4)
    path = './static/assets/DCF/'+ ticker + '/balance_sheet.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(balance_sheet, f, ensure_ascii=False, indent=4)
    path = './static/assets/DCF/'+ ticker + '/cash_flow_quar.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(cash_flow_quar, f, ensure_ascii=False, indent=4)
    path = './static/assets/DCF/'+ ticker + '/cash_flow.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(cash_flow, f, ensure_ascii=False, indent=4)
    path = './static/assets/DCF/'+ ticker + '/EV.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(EV, f, ensure_ascii=False, indent=4)
    path = './static/assets/DCF/'+ ticker + '/income_statement.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(income_statement, f, ensure_ascii=False, indent=4)
    path = './static/assets/DCF/'+ ticker + '/profile.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(profile, f, ensure_ascii=False, indent=4)
    path = './static/assets/DCF/'+ ticker + '/income_statement_quar.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(income_statement_quar, f, ensure_ascii=False, indent=4)
    path = './static/assets/DCF/'+ ticker + '/market_return.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(market_return, f, ensure_ascii=False, indent=4)

    
    path = './static/assets/DCF/TICKER_LIST/ticker_list.json'
    with open(path) as json_file:
        ticker_list = json.load(json_file)
    ticker_list.append(ticker)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(ticker_list, f, ensure_ascii=False, indent=4)

    