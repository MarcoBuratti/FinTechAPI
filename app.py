from flask import Flask, request, jsonify, render_template
import sqlite3
from manageDB import dbConnection
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import Form, StringField, TextAreaField, PasswordField, validators

app = Flask(__name__)
conn = dbConnection()
cursor = conn.cursor()


@app.route('/getUser', methods=['GET'])
def getBook():
    if request.method == 'GET':
        try:
            cursor = conn.execute('SELECT * FROM User')
        except sqlite3.IntegrityError as e:
            print(e)
        users = [ dict(id=row[0], mail=row[1]) for row in cursor.fetchall() ]
        if users is not None:
            return jsonify(users), 200
        else:
            return jsonify([{'error':'Nothing Found'}])

@app.route('/postUser', methods=['POST'])    
def putBook():
    if request.method == 'POST':
        mail = request.form['mail']
        password = request.form['password']

        mail = '\''+ mail + '\'' + ', '
        password =  mail + '\'' + generate_password_hash(password, method='SHA256') + '\''
        cursor = conn.execute('select max(id), mail from User')
        users = [ dict(id=row[0], mail=row[1]) for row in cursor.fetchall() ]
        lastID = str(users[0]['id'] + 1)
        query = 'INSERT INTO User (id, mail, password) VALUES ( ' + lastID + ', ' + str(password) + ')'
        try:
            cursor = conn.execute( str(query) )
            conn.commit()
        except sqlite3.IntegrityError as e:
            print(e)
        return jsonify([{'respone': "account created, user posted"}]), 200
        
@app.route('/delUser/<int:id>', methods=['DELETE'])    
def deleteBook(id):
    if request.method == 'DELETE':
        try:
            sqlQuery = """DELETE FROM User WHERE id=?"""
            cursor =  conn.execute(sqlQuery, (id,))
            conn.commit()
            return 'The User with the ID: {} has been deleted.'.format(id), 200
        except sqlite3.DatabaseError as e:
            print(e)
        

@app.route('/')
def index():
    return render_template('home.html')

# Register Form Class
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        return render_template('register.html', form=form)
    return render_template('register.html', form=form)
    
    

@app.route('/setDB')
def setDB():
    try:
        cursor = conn.execute("""INSERT INTO User (id, mail, password) VALUES (0, 'admin@mail.com', 'FinTechAPI')""")
        conn.commit()
    except sqlite3.IntegrityError as e:
        print(e)
    return jsonify([{'response':'Set the DB'}])



if __name__ == '__main__':
    app.run(debug=True)
