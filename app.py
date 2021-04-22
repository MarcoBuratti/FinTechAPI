from flask import Flask, request, jsonify, render_template, flash, redirect, url_for, session
import sqlite3
from manageDB import dbConnection
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from functools import wraps
import requests
from utils.stock import *
from utils.financial import *
from utils.chatbot import *
from utils.dcfFunctions import *
import datetime


app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key='secret123'
conn = dbConnection()
cursor = conn.cursor()
stock = Stock()
chatbot = Chat()

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        mail = request.form['mail']
        password = request.form['password']
        name = request.form['name']
        try:
            cursor = conn.execute('SELECT id, mail FROM User WHERE mail=\'' + str(mail) + '\'')
            result = [ dict(id=row[0], mail=row[1]) for row in cursor.fetchall() ]
        except sqlite3.InterfaceError as e:
            print(e)
            
        if len(mail) < 4 or  result != []:
            flash('Email must be greater than three characters or the email addreas has been taken.', 'danger')
        elif len(name) < 2:
            flash('First name must be greater than one character.', 'danger')
        elif len(password) < 6:
            flash('Password must be at least six characters.', 'danger')
        else:
            name = '\''+ name + '\'' + ', '
            mail = name + '\''+ mail + '\'' + ', '
            password =  mail + '\'' + generate_password_hash(password, method='SHA256') + '\''
            cursor = conn.execute('select max(id), mail from User')
            users = [ dict(id=row[0], mail=row[1]) for row in cursor.fetchall() ]
            lastID = str(users[0]['id'] + 1)
            query = 'INSERT INTO User (id, name, mail, password) VALUES ( ' + lastID + ', ' + str(password) + ')'
            try:
                cursor = conn.execute( str(query) )
                conn.commit()
            except sqlite3.IntegrityError as e:
                print(e) 
            flash('you are now register', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        mail = request.form['mail']
        password_user = request.form['password']
        try:
            cursor = conn.execute('SELECT mail, password FROM User WHERE mail=\'' + str(mail) + '\'')            
            data = [ dict(mail=row[0], password=row[1]) for row in cursor.fetchall() ]
            password = ''
            if len(data) > 0:
                password = data[0]['password']
            # Compare Passwords
            if check_password_hash(password, password_user):
                # Passed
                session['logged_in'] = True
                session['mail'] = mail

                flash('You are now logged in', 'success')
                return render_template('home.html')
            else:
                error = 'Invalid mail or password'
                return render_template('login.html', error=error)
        except sqlite3.DatabaseError as e:
            print(e)
            error = 'Mail not found'
            return render_template('home.html')
    return render_template('login.html')

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('index'))

@app.route('/news', methods=['GET'])
@is_logged_in
def news():
    mail = session['mail']
    try:
        cursor = conn.execute('SELECT id FROM User WHERE mail=\'' + str(mail) + '\'')
        userID = str(cursor.fetchall()[0][0])
    except sqlite3.InterfaceError as e:
            print(e)
    try:
        cursor = conn.execute('SELECT ticker FROM UserPF WHERE id=\'' + userID + '\'')
        tickerResult = [ row[0] for row in cursor.fetchall() ]
    except sqlite3.IntegrityError as e:
        print(e)

    if len(tickerResult) < 1:
        flash('You have to add at least one Ticker to your Watch List to use this function', 'danger')
        return redirect(url_for('personalArea'))
    else:
        news = []
        for t in tickerResult:
            url = 'https://financialmodelingprep.com/api/v3/stock_news?tickers=' + t + '&limit=50&apikey=ee017fc9ea512948dafef934f2fc8565' 
            response = requests.get(url).json()
            sublist = []
            for i in range(3):
                o = {
                'title': response[i]['title'],
                'description':response[i]['text'],
                'author':response[i]['site'],
                'publishedAt':response[i]['publishedDate'][:-10],
                'urlToImage':response[i]['image'],
                'url': response[i]['url'],
                'symbol': response[i]['symbol']
                }
                #news.append(o)
                sublist.append(o)
            news.append(sublist)
            
        return render_template('displayNews.html', news=news)

@app.route('/setDB')
def setDB():
    try:
        cursor = conn.execute("""INSERT INTO User (id, name, mail, password) VALUES (0, 'Admin', 'admin@mail.com', 'FinTechAPI')""")
        conn.commit()
    except sqlite3.IntegrityError as e:
        print(e)
    return jsonify([{'response':'Set the DB'}])

@app.route('/quant', methods=['GET'])
@is_logged_in
def portfolio():
    mail = session['mail']
    try:
        cursor = conn.execute('SELECT id FROM User WHERE mail=\'' + str(mail) + '\'')
        userID = str(cursor.fetchall()[0][0])
    except sqlite3.InterfaceError as e:
            print(e)
    try:
        cursor = conn.execute('SELECT ticker FROM UserPF WHERE id=\'' + userID + '\'')
        tickerResult = [ row[0] for row in cursor.fetchall() ]
    except sqlite3.IntegrityError as e:
        print(e)

    if len(tickerResult) < 2:
        flash('You have to add at least two Ticker to your Watch List to use this function', 'danger')
        return redirect(url_for('personalArea'))
    else:
        data2 = datetime.datetime.today().strftime('%Y-%m-%d')
        data1 = datetime.date.today() - datetime.timedelta(days=365)

        stock.initData(tickerResult, data1=data1, data2=data2)
        markovitz = stock.markovitz()
        logRet = stock.logRet(data1, data2)
        return render_template('portfolio.html', markovitz=markovitz, logRet=logRet)

@app.route('/personal-area', methods=['GET', 'POST'])
@is_logged_in
def personalArea():
    if request.method == 'POST':
        addTicker = request.form['addTicker']
        delTicker = request.form['delTicker']
        if len(addTicker) == 0 and len(delTicker) == 0:
            flash('You have to add at least one Ticker in the box', 'danger')
            return redirect(url_for('personalArea'))
        mail = session['mail']
        try:
            cursor = conn.execute('SELECT id FROM User WHERE mail=\'' + str(mail) + '\'')
            userID = str(cursor.fetchall()[0][0])
        except sqlite3.InterfaceError as e:
            print(e)

        if len(addTicker) > 0:
            addTicker = '\'' + str(addTicker.upper()) + '\''

            try:
                query = 'INSERT INTO UserPF (id, ticker) VALUES ( ' + userID + ', ' + addTicker + ')'
                cursor = conn.execute( query )
                conn.commit()
            except sqlite3.IntegrityError as e:
                print(e)
            try:
                cursor = conn.execute('SELECT ticker FROM UserPF WHERE id=\'' + userID + '\'')
                tickerResult = [ row[0] for row in cursor.fetchall() ]
            except sqlite3.IntegrityError as e:
                print(e)
        
        if len(delTicker) > 0:
            delTicker = '\'' + str(delTicker.upper()) + '\''
            try:
                query = 'DELETE FROM UserPF WHERE id=' + userID + ' and ticker=' + delTicker
                cursor =  conn.execute( query )
                conn.commit()
            except sqlite3.IntegrityError as e:
                print(e)
            try:
                cursor = conn.execute('SELECT ticker FROM UserPF WHERE id=\'' + userID + '\'')
                tickerResult = [ row[0] for row in cursor.fetchall() ]
            except sqlite3.IntegrityError as e:
                print(e)

        company_name = []
        for t in tickerResult:
            url = "http://d.yimg.com/autoc.finance.yahoo.com/autoc?query={}&region=1&lang=en".format(t)
            result = requests.get(url).json()['ResultSet']['Result'][0]
            o = {
                'name': result['name'],
                'ticker': result['symbol'],
                'exchange': result['exchDisp']
            }
            company_name.append(o)
        
        return render_template('personalArea.html', ticker=company_name)

    mail = session['mail']
    try:
        cursor = conn.execute('SELECT id FROM User WHERE mail=\'' + str(mail) + '\'')
        userID = str(cursor.fetchall()[0][0])
    except sqlite3.InterfaceError as e:
            print(e)
    try:
        cursor = conn.execute('SELECT ticker FROM UserPF WHERE id=\'' + userID + '\'')
        tickerResult = [ row[0] for row in cursor.fetchall() ]
    except sqlite3.IntegrityError as e:
        print(e)

    company_name = []
    for t in tickerResult:
        url = "http://d.yimg.com/autoc.finance.yahoo.com/autoc?query={}&region=1&lang=en".format(t)
        result = requests.get(url).json()['ResultSet']['Result'][0]
        o = {
            'name': result['name'],
            'ticker': result['symbol'],
            'exchange': result['exchDisp']
        }
        company_name.append(o)
    
    return render_template('personalArea.html', ticker=company_name)

@app.route('/financials', methods=['GET', 'POST'])
@is_logged_in
def financials():
    listaSector = []
    listaExchange = []
    #stockPrice = ['5$', '10$', '20$', '50$', '100$', '200$', '500$', '1000$', '+5000$']
    marketCapDimension = ['Micro ($50mln to $300mln)', 'Small ($300mln to $2bln)', 'Mid ($2bln to $10bln)', 'Large ($10bln to $200bln)', 'Mega ($200bln and more)']
    with open('./static/assets/sector.json') as f:
        dataJson = json.load(f)
    for i in range(len(dataJson)):
        listaSector.append(dataJson[i]['sector'])

    with open('./static/assets/exchange.json') as f:
        dataJson = json.load(f)
    for i in range(len(dataJson)):
        listaExchange.append(dataJson[i]['exchange'])

    if request.method == 'POST':
        exchange = request.form.get('exchange')
        sector = request.form.get('sector')
        price = request.form.get('price')
        ticker = request.form.get('ticker')
        tickerList = []
        marketCapList = []
        nameList = []
        priceList = []
        switcher = {
            'Micro ($50mln to $300mln)': [0, 300000000],
            'Small ($300mln to $2bln)': [300000000, 2000000000],
            'Mid ($2bln to $10bln)': [2000000000, 10000000000],
            'Large ($10bln to $200bln)': [10000000000, 200000000000],
            'Mega ($200bln and more)': [200000000000, 20000000000000]
        }

        with open('./static/assets/stockData.json') as f:
            dataJson = json.load(f)
        bigList = []
        for i in range(len(dataJson)):
           if dataJson[i]['exchange'] == exchange and dataJson[i]['sector'] == sector \
                and dataJson[i]['marketCap'] > switcher[price][0] and dataJson[i]['marketCap'] < switcher[price][1]:

               o = {
                   'ticker':dataJson[i]['ticker'],
                   'marketCap':dataJson[i]['marketCap'],
                   'name':dataJson[i]['name'],
                   'price':dataJson[i]['price']
               }
               bigList.append(o)
        if ticker != None:
            finHealth = draw_bars(ticker)
            exchange = get_exchange(ticker)
            description = getDescription(ticker)
            revenues = draw_lines(ticker)
            indicator = draw_indicators(ticker)
            stringa = str(exchange + ':' + ticker)
            figDCF = dcf(ticker)
            link = {
                'ticker': stringa
            }
            descriptionFinancialHealth = 'The considered graph gives a snapshot about the long and short-term assets and liabilities company situation.'
            return render_template('financials.html',  descriptionFinancialHealth=descriptionFinancialHealth, figDCF=figDCF, link=link, listaExchange=listaExchange, listaSector=listaSector, stockPrice=marketCapDimension, bigList=bigList, finHealth=finHealth, result=ticker, description=description, revenues=revenues, indicator=indicator)
        else:
            return render_template('financials.html', listaExchange=listaExchange, listaSector=listaSector, stockPrice=marketCapDimension, bigList=bigList)
    
    return render_template('financials.html', listaExchange=listaExchange, listaSector=listaSector, stockPrice=marketCapDimension)

@app.route('/main')
def main():
    return render_template('main.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route("/Chatbot")
def home():
    return render_template("chat.html")

@app.route("/get")
def get_bot_response():

    userText = request.args.get('msg')
    ciao = chatbot.get_answer(userText)
    
    return str(ciao)

if __name__ == '__main__':  
    app.run()