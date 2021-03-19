from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

@app.route('/getBook/<int:id>', methods=['GET'])
def getBook(id):
    conn = dbConnection()
    cursor = conn.cursor()
    book = None
    if request.method == 'GET':
        cursor = conn.execute('SELECT * FROM book WHERE id=?', (id,))
        rows = cursor.fetchall()
        for r in rows:
            book = r
        if book is not None:
            return jsonify(book), 200
        else:
            return jsonify([{'book':'Not Found'}]), 200

@app.route('/putBook/<int:id>', methods=['PUT'])    
def putBook(id):
    conn = dbConnection()
    cursor = conn.cursor()
    if request.method == 'PUT':
        author = request.form['author']
        language = request.form['language']
        title = request.form['title']
        sqlQuery = """UPDATE book SET author=?, language=?, title=? WHERE id=?"""

        update_book = {
            'id': id,
            'author': author,
            'title': title,
            'language': language
        }                

        cursor =  conn.execute(sqlQuery, (author, language, title, id))
        conn.commit()
        return jsonify(update_book), 200
        
@app.route('/delBook/<int:id>', methods=['DELETE'])    
def deleteBook(id):
    conn = dbConnection()
    cursor = conn.cursor()
    if request.method == 'DELETE':
        sqlQuery = """DELETE FROM book WHERE id=?"""
        cursor =  conn.execute(sqlQuery, (id,))
        conn.commit()
        return 'The book with the ID: {} has been deleted.'.format(id), 200


@app.route('/books', methods=['GET', 'POST'])
def index():
    conn = dbConnection()
    cursor = conn.cursor()

    if request.method == 'GET':
        cursor = conn.execute('SELECT * FROM book')
        books = [
            dict(id=row[0], author=row[1], language=row[2], title=row[3])
            for row in cursor.fetchall()
        ]
        if books is not None:
            return jsonify(books)
        else:
            'Nothing Found', 404
    
    if request.method == 'POST':
        new_author = request.form['author']
        new_lang = request.form['language']
        new_title = request.form['title']
        sqlQuery = """INSERT INTO book (author, language, title)
                        VALUES (?, ?, ?)"""

        cursor =  conn.execute(sqlQuery, (new_author, new_lang, new_title))
        conn.commit()
        return f'Book with the ID: {cursor.lastrowid} created succesfully'


def dbConnection():
    conn = None
    try:
        conn = sqlite3.connect('books.sqlite')
    except sqlite3.error as e:
        print(e)
    return conn

if __name__ == '__main__':
    app.run()
