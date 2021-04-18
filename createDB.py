import sqlite3

conn = sqlite3.connect('FINTECH.sqlite')


cursor = conn.cursor()
userTable = """ CREATE TABLE User (
    id INT NOT NULL, 
    name CHAR(50) NOT NULL,
    mail CHAR(50) NOT NULL,
    password CHAR(50) NOT NULL,
    PRIMARY KEY(mail)
)"""

userPortfolioTable = """ CREATE TABLE UserPF (
    id INT NOT NULL,
    ticker CHAR(500) NOT NULL
)"""

cursor.execute(userTable)
cursor.execute(userPortfolioTable)