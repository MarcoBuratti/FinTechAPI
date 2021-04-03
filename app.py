from flask import Flask, request, jsonify, render_template, flash, redirect, url_for, session
import sqlite3
from manageDB import dbConnection
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from functools import wraps
import requests
from utils.stock import *
from utils.dcf import *

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key='secret123'
conn = dbConnection()
cursor = conn.cursor()
stock = Stock()

@app.route('/getUser', methods=['GET'])
def getUser():
    if request.method == 'GET':
        try:
            cursor = conn.execute('SELECT * FROM User')
        except sqlite3.IntegrityError as e:
            return jsonify([{'error': str(e)}])
        users = [ dict(id=row[0], name=row[1], mail=row[2]) for row in cursor.fetchall() ]
        if users is not None:
            return jsonify(users), 200
        else:
            return jsonify([{'error':'Nothing Found'}])
        
@app.route('/delUser/<int:id>', methods=['DELETE'])    
def deleteUser(id):
    if request.method == 'DELETE':
        try:
            cursor =  conn.execute('DELETE FROM User WHERE id=?', (id,))
            conn.commit()
            return 'The User with the ID: {} has been deleted.'.format(id), 200
        except sqlite3.DatabaseError as e:
            return jsonify([{'error': str(e)}])

@app.route('/')
def index():
    return render_template('home.html')
    
class CompanyForm(Form):
    ticker = StringField('ticker', [validators.Length(min=1, max=50)])

@app.route('/company', methods = ['GET','POST'])
def getCompany():
    form = CompanyForm(request.form)
    if request.method == 'POST':
        ticker = request.form['ticker']
        
    return render_template('company.html', form = form)
@app.route('/contactUs')
def contact():
    return render_template('contactUs.html')

class RegisterForm(Form):
    name = StringField('name', [validators.Length(min=1, max=50)])
    mail = StringField('mail', [validators.Length(min=6, max=50)])
    password = PasswordField('password', [validators.Length(min=6, max=50)])
    confirm = PasswordField('Confirm Password')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
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
            return render_template('login.html', form=form)

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = RegisterForm(request.form)
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
                return render_template('login.html', error=error, form=form)
        except sqlite3.DatabaseError as e:
            print(e)
            error = 'Mail not found'
            return render_template('home.html', error=error)
    return render_template('login.html', form=form)

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

# Logout
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

    news = []
    for t in tickerResult:
        url = 'https://financialmodelingprep.com/api/v3/stock_news?tickers=' + t + '&limit=50&apikey=1c0254f41fa369f54c93e476c375529e' 
        response = requests.get(url).json()
        for i in range(2):
            o = {
            'title': response[i]['title'],
            'description':response[i]['text'],
            'author':response[i]['site'],
            'publishedAt':response[i]['publishedDate'][:-10],
            'urlToImage':response[i]['image'],
            'url': response[i]['url'],
            'symbol': response[i]['symbol']
            }
            news.append(o)
        
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
        weights = [ 1/len(tickerResult) for elem in tickerResult ]
    except sqlite3.IntegrityError as e:
        print(e)

    stock.initData(tickerResult, weights)
    annualReturnW, volatility, amount = stock.recapPortfolio()
    annual_returns, tickers = stock.recapStock()
    messages = []
    messages.append('The annual return of the portfolio is: ' + str(round(annualReturnW, 3)) + '%\n')
    messages.append('The volatility of the porfolio is: ' + str( round( (volatility*100), 2) ) + '%\n' + 'The amount of your portfolio is: ' + str( round(amount, 2) ) + '$\n')
    for i in range(len(annual_returns)):
        messages.append('The single annual return of the stock ' + tickers[i] + ' is ' + str( round(annual_returns.get(i)*100, 2) ) + '%\n' )
    
    return render_template('portfolio.html', messages=messages)

@app.route('/personal-area', methods=['GET', 'POST'])
@is_logged_in
def personalArea():
    if request.method == 'POST':
        mail = session['mail']
        try:
            cursor = conn.execute('SELECT id FROM User WHERE mail=\'' + str(mail) + '\'')
            userID = str(cursor.fetchall()[0][0])
        except sqlite3.InterfaceError as e:
            print(e)
        addTicker = request.form['addTicker']
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
        
        delTicker = request.form['delTicker']
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

@app.route('/financials', methods=['GET'])
@is_logged_in
def financials():
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

    #graphJSON = []
    #for t in tickerResult:
    #    graphJSON.append(dcf(t))

    graphJSON = dcf(tickerResult[0])
    return render_template('financials.html', plot=graphJSON)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':  
    app.run()