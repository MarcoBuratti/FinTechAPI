from flask import Flask, request, jsonify, render_template, flash, redirect, url_for, session
import sqlite3
from manageDB import dbConnection
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key='secret123'
conn = dbConnection()
cursor = conn.cursor()


@app.route('/getUser', methods=['GET'])
def getBook():
    if request.method == 'GET':
        try:
            cursor = conn.execute('SELECT * FROM User')
        except sqlite3.IntegrityError as e:
            print(e)
        users = [ dict(id=row[0], name=row[1], mail=row[2]) for row in cursor.fetchall() ]
        if users is not None:
            return jsonify(users), 200
        else:
            return jsonify([{'error':'Nothing Found'}])
        
@app.route('/delUser/<int:id>', methods=['DELETE'])    
def deleteBook(id):
    if request.method == 'DELETE':
        try:
            cursor =  conn.execute('DELETE FROM User WHERE id=?', (id,))
            conn.commit()
            return 'The User with the ID: {} has been deleted.'.format(id), 200
        except sqlite3.DatabaseError as e:
            print(e)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        mail = request.form['mail']
        password = request.form['password']
        name = request.form['name']
        if len(mail) < 4:
            return jsonify([{'response':'Email must be greater than three characters.'}])
        elif len(name) < 2:
            return jsonify([{'response':'First name must be greater than one character.'}])
        elif len(password) < 7:
            return jsonify([{'response':'Password must be at least seven characters.'}])
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
            return jsonify([{'respone': "account created, user posted"}]), 200

    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        mail = request.form['mail']
        password_user = request.form['password']

        # Get user by username
        try:
            result = cursor.execute("SELECT * FROM User WHERE mail=?", (mail))

            if result > 0:
                # Get stored hash
                data = cursor.fetchone()
                password = data['password']

                # Compare Passwords
                if check_password_hash(password_user, password):
                    # Passed
                    session['logged_in'] = True
                    session['username'] = mail

                    flash('You are now logged in', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    error = 'Invalid password'
                    return render_template('login.html', error=error)
        except sqlite3.DatabaseError as e:
            error = 'Mail not found'
            return render_template('login.html', error=error)

    return render_template('login.html')

@app.route('/setDB')
def setDB():
    try:
        cursor = conn.execute("""INSERT INTO User (id, name, mail, password) VALUES (0, 'Admin', 'admin@mail.com', 'FinTechAPI')""")
        conn.commit()
    except sqlite3.IntegrityError as e:
        print(e)
    return jsonify([{'response':'Set the DB'}])



if __name__ == '__main__':  
    app.run(debug=True)