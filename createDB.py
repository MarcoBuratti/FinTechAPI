import sqlite3

conn = sqlite3.connect('FINTECH.sqlite')


cursor = conn.cursor()
userTable = """ CREATE TABLE User (
    id INT NOT NULL, 
    mail CHAR(50) NOT NULL,
    password CHAR(50) NOT NULL,
    PRIMARY KEY(mail)
)"""

userPortfolioTable = """ CREATE TABLE UserPF (
    id INT PRIMARY KEY,
    ticker CHAR(500) NOT NULL
)"""

telegramTable = """ CREATE TABLE telegram (
    id INT PRIMARY KEY NOT NULL,
    telephone CHAR(10) NOT NULL
)"""

cursor.execute(userTable)
cursor.execute(userPortfolioTable)
cursor.execute(telegramTable)
