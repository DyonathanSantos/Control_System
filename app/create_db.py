import sqlite3
import os
import datetime
import shutil

# -------------------------------
# 🔌 Conexão com o banco
# -------------------------------
DB_PATH = "base.db"
def connect():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

con = connect() # open connection
cur = con.cursor()


cur.execute('''CREATE TABLE IF NOT EXISTS stock( 
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            product TEXT NOT NULL UNIQUE, category TEXT, quantity INTEGER DEFAULT 0, 
            buy REAL DEFAULT 0.0,
            sell REAL DEFAULT 0.0
             )''') # Stock

cur.execute('CREATE INDEX IF NOT EXISTS idx_stock_product ON stock(product)') # index of stock for fast find

cur.execute('''CREATE TABLE IF NOT EXISTS comanda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer TEXT,
            status TEXT DEFAULT 'open',
            data TEXT DEFAULT (datetime('now','localtime')))''') # Comanda for customer register    

cur.execute('CREATE INDEX IF NOT EXISTS idx_comanda_id ON comanda(id)') # index of comanda

cur.execute('''CREATE TABLE IF NOT EXISTS item_comanda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_comanda INTEGER,
            id_product INTEGER,
            product TEXT,
            quantity INTEGER,
            price REAL,
            FOREIGN KEY (id_comanda) REFERENCES comandas(id),
            FOREIGN KEY (id_product) REFERENCES product(id)
            )''') # save the product in comanda for late list

cur.execute('''CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT,
            role TEXT -- admin or staff
            )''') # Table of employee

cur.execute('''CREATE TABLE IF NOT EXISTS sells (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT DEFAULT (datetime('now','localtime')),
            product TEXT,
            quantity INTEGER,
            price REAL,
            total REAL
            )''') # for sell in day ou mouth 

cur.execute('CREATE TABLE IF NOT EXISTS logs(user TEXT, action TEXT)') # Table for register logs

cur.execute('CREATE INDEX IF NOT EXISTS idx_username_users ON users(username)') # index of USERS

con.close() #close connection
