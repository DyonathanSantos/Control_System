from create_db import connect
import sqlite3
import pandas as pd
import hashlib


#Create

def hash_password(password):
   return hashlib.sha256(password.encode()).hexdigest()

def add_product_stock(product, quantity, category, buy, sell):
    
    try:
        with connect() as con:
          cur = con.cursor()
          cur.execute('''INSERT INTO stock (product,quantity, category, buy, sell)
                      VALUES (?, ?, ?, ?, ?) ''',(product.upper(), quantity, category.upper(), buy, sell)) #add items in stock
          con.commit()
    except sqlite3.IntegrityError as e:
       raise # handle unique constraint etc (DB error) 
    except  Exception as e:
       raise     

def add_comanda(name):
   
   try:
      with connect() as con:
         cur = con.cursor()
         cur.execute('''INSERT INTO comanda (customer) VALUES (?)''',(name.upper(),))
         con.commit()
   except Exception as e:
      raise

def register_sale(product, quantity, price):
   try:
      with connect() as con:
         cur = con.cursor()
         total = quantity * price
         cur.execute('''INSERT INTO sells (product, quantity, price, total)
                     VALUES (?,?,?,?)''',(product.upper(), quantity, price, total))
      # update stock
         cur.execute('SELECT quantity FROM stock WHERE product = ?',(product.upper(),))
         stock_q = cur.fetchone()
         if stock_q[0] < quantity:
            raise ValueError('Not enough stock')
         new_q = stock_q[0] - quantity 
         if new_q <=5:
            cur.execute('UPDATE stock SET quantity = ?',(new_q,))
            print('Low stock <= 5 \n Registered sell')
         else:
            cur.execute('UPDATE stock SET quantity = ?',(new_q,)) 
         con.commit()
   except Exception as e:
        raise

def add_item_comanda(id_comanda, id_product, quantity):
   with connect() as con:
      #fetch price and stock
      cur = con.cursor()
      cur.execute('SELECT product, quantity, sell FROM stock WHERE id = ?',(id_product,))
      row = cur.fetchone()

      if not row:
         raise ValueError("Product not found")
      price = row[2]
      stock = row[1]

      if stock < quantity:
         raise ValueError('Not enough stock')
      #update item (insert or update)

      cur.execute('''SELECT id, quantity FROM item_comanda WHERE id_comanda = ? AND id_product = ?
                  ''',(id_comanda,id_product))
      item  = cur.fetchone()

      if item:
         new_q = item[1] + quantity
         cur.execute('UPDATE item_comanda SET quantity = ? WHERE id = ?',(new_q, item[0],))
      else:
         cur.execute('''INSERT INTO item_comanda (id_comanda, id_product, product, quantity, price)
                     VALUES (?, ?, ?, ?, ?)''',(id_comanda, id_product, row[0], quantity, price))
      #update stock
      new_quantity_stock = row[1] - quantity
      cur.execute('UPDATE stock SET quantity = ? WHERE id = ?',(new_quantity_stock, id_product))
      con.commit()

def register_log(user, action):
      with connect() as con:
         cur = con.cursor()
         cur.execute('INSERT INTO logs (user,action) VALUES (?, ?)',(user,action))
         con.commit()

def register_user(username, password, role='user'):
   try:
      hashed = hash_password(password)
      with connect() as con:
         cur = con.cursor()
         cur.execute('''INSERT INTO users (username, password_hash, role)
                     VALUES (?, ?, ?)''',(username, hashed, role.lower(),))
         con.commit()
         return True
   except sqlite3.IntegrityError as e:
      raise ValueError ('User already registered')
      

# READ --------------------

def see_stock():
   with connect() as con:
      cur = con.cursor()
      df = pd.read_sql_query('SELECT * FROM stock',con)
   return df

def see_comanda():
   with connect() as con:
      cur = con.cursor()
      df = pd.read_sql_query('SELECT * FROM comanda WHERE status = "open"',con)
   return df

def see_close_comanda():
   with connect() as con:
      cur = con.cursor()
      df = pd.read_sql_query('SELECT * FROM comanda WHERE status = "close"',con)
   return df


def see_item_comanda(id_comanda):
   with connect() as con:
      cur = con.cursor()
      df = pd.read_sql_query('''SELECT product, quantity, price, quantity * price AS total
                           FROM item_comanda WHERE id_comanda = ? ''', con, params=(id_comanda,))
#Format decimals
      df["price"] = df["price"].round(2)
      df["total"] = df["total"].round(2)
      df['pagamento'] = sum(df['total'])
      return df
   
def see_saler():
   with connect() as con:
      cur = con.cursor()
      df = pd.read_sql_query('SELECT * FROM sells',con)
      return df
   
def see_logs():
   with connect() as con:
      cur = con.cursor()
      df = pd.read_sql_query('SELECT * FROM logs',con)
      return df
def see_user():
   with connect() as con:
      cur = con.cursor()
      df = pd.read_sql_query("SELECT id, username, role FROM users",con)
      return df


#UPDATE

def update_stock(id_product, quantity):
      with connect() as con:
         cur = con.cursor()
         cur.execute('SELECT id, quantity FROM stock WHERE id = ?',(id_product,))
         item = cur.fetchone() 
         new_q = item[1] + quantity
         cur.execute('UPDATE stock SET quantity = ? WHERE id = ?',(new_q, item[0],))
         con.commit()

def close_comanda(id_comanda, user):
      try:
         with connect() as con:
            cur = con.cursor()
   #Change status
            #cur.execute('UPDATE comanda SET status ="close" WHERE id = ?',(id_comanda,)) 
            #con.commit()
   #Register Sale
            cur.execute("SELECT product, quantity, price FROM item_comanda WHERE id_comanda = ?",(id_comanda,))
            register = cur.fetchone()
            product = register[0]
            quantity = register [1]
            price = register[2]



   #Register log and sum total
            #cur.execute('SELECT SUM(price * quantity) FROM item_comanda WHERE id_comanda = ?',(id_comanda,))
            #total = cur.fetchone()[0] or 0
            #register_log(user, f'Close the comanda {id_comanda} with total {total}')
            return print(product,quantity, price)
      except Exception as e:
         print("❌ Error closing comanda:", e)


def login_user(username, password):
   hashed = hash_password(password)
   with connect() as con:
      cur = con.cursor()
      cur.execute('SELECT * FROM users WHERE username = ? AND password_hash = ?',(username, hashed))
      return cur.fetchone()
      
 #DELETE 

def delete_comanda(id_comanda):
   with connect() as con:
      cur = con.cursor()
      cur.execute('DELETE FROM comanda WHERE id = ?',(id_comanda,))
      con.commit()


def delete_stock(id_product):
   with connect() as con:
      cur = con.cursor()
      cur.execute('DELETE FROM stock WHERE id = ?',(id_product,))
      con.commit()

def delete_user(id_user):
   with connect() as con:
      cur = con.cursor()
      cur.execute("DELETE FROM users WHERE id = ?",(id_user,))
      con.commit()



