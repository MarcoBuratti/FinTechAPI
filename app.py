from flask import Flask, request, jsonify, render_template, flash, redirect, url_for, session
import sqlite3
from manageDB import dbConnection
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from functools import wraps
import requests

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key='secret123'
conn = dbConnection()
cursor = conn.cursor()

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
    if request.method == 'POST':
        mail = request.form['mail']
        password = request.form['password']
        name = request.form['name']
        if len(mail) < 4:
            flash('Email must be greater than three characters.', 'danger')
        elif len(name) < 2:
            return jsonify([{'response':'First name must be greater than one character.'}])
        elif len(password) < 6:
            return jsonify([{'response':'Password must be at least six characters.'}])
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
                return jsonify([{'error': str(e)}])
            flash('you are now register', 'success')
            return render_template('home.html')
    form = RegisterForm(request.form)
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
    return redirect(url_for('login'))

class NewsForm(Form):
    company = StringField('company', [validators.Length(min=1, max=50)])
    ticker = StringField('ticker', [validators.Length(min=6, max=50)])
    confirm = PasswordField('Confirm Password')    

@app.route('/news', methods=['GET', 'POST'])
@is_logged_in
def news():
    form = NewsForm(request.form)
    if request.method == 'POST':
        company = request.form['company']
        ticker = request.form['ticker']
        
        url = ('https://newsapi.org/v2/everything?q=' + str(company) + '&domains=bloomberg.com&apiKey=923719faca26405ab3062a0dcfd400ae')
        response = requests.get(url)
        response = response.json()
        news = []
        for i in range(len(response['articles'])):
            obj = {
            'title': response['articles'][i]['title'],
            'description':response['articles'][i]['description'],
            'author':response['articles'][i]['author'],
            'publishedAt':response['articles'][i]['publishedAt'][:-10],
            'urlToImage':response['articles'][i]['urlToImage'],
            'url': response['articles'][i]['url']
            }
            news += [obj]
        return render_template('displayNews.html', news=news)

    return render_template('news.html', form=form)

@app.route('/setDB')
def setDB():
    try:
        cursor = conn.execute("""INSERT INTO User (id, name, mail, password) VALUES (0, 'Admin', 'admin@mail.com', 'FinTechAPI')""")
        conn.commit()
    except sqlite3.IntegrityError as e:
        print(e)
    return jsonify([{'response':'Set the DB'}])

if __name__ == '__main__':  
    app.run()