from create_db import connect
import sqlite3
import pandas as pd


#Create

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
         con.commit()
   except Exception as e:
        raise

def add_item_comanda(id_comanda, id_product,quantity):
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
         cur.execute('UPDATE item_comanda SET quantity = ? WHERE id = ?'(new_q, item[0]))
      else:
         cur.execute('''INSERT INTO item_comanda (id_comanda, id_product, product, quantity, price)
                     VALUES (?, ?, ?, ?, ?)''',(id_comanda, id_product, row[0], quantity, price))
      #update stock

      cur.execute('UPDATE stock SET quantity = ? WHERE id = ?',(quantity, id_product))
      con.commit()

def register_log(user,action):
      with connect as con:
         cur = con.cursor()
         cur.execute('INSERT INTO logs (user,action) VALUES (?, ?)',(user,action))
         con.commit()


# READ -------------------- (late remove the print function)

def see_stock():
   with connect() as con:
      cur = con.cursor()
      df = pd.read_sql_query('SELECT * FROM stock',con)
   return print(df)

def see_comanda():
   with connect() as con:
      cur = con.cursor()
      df = pd.read_sql_query('SELECT * FROM comanda WHERE status = "open"',con)
   return print(df)

def see_item_comanda(id_comanda):
   with connect() as con:
      cur = con.cursor()
      df = pd.read_sql_query('''SELECT product, quantity, price, quantity * price AS total
                           FROM item_comanda WHERE id_comanda = ? ''', con, params=(id_comanda,))
#Format decimals
      df["price"] = df["price"].round(2)
      df["total"] = df["total"].round(2)
      return print(df)
   
def see_saler():
   with connect() as con:
      cur = con.cursor()
      df = pd.read_sql_query('SELECT * FROM sells',con)
      return print(df)
   
def see_logs():
   with connect()as con:
      cur = con.cursor()
      df = pd.read_sql_query('SELECT * FROM logs',con)
      return print(df)

#UPDATE

def update_stock(id_product, quantity):
      with connect() as con:
         cur = con.cursor()
         cur.execute('SELECT id, quantity FROM stock WHERE id = ?',(id_product,))
         item = cur.fetchone() 
         new_q = item[1] + quantity
         cur.execute('UPDATE stock SET quantity = ? WHERE id = ?',(new_q, item[0]))
         con.commit()

def close_comanda(id_comanda,user):
      
      with connect() as con:
         cur = con.cursor()
         see_item_comanda(id_comanda)
         register_log(user, f'Close the comanda {id_comanda} with total {total:.2f}')  
         con.commit()
      


 #DELETE 

def delete_comanda(id_comanda):
   with connect() as con:
      cur = con.cursor('DELETE FROM comanda WHERE id = ?',(id_comanda,))
      con.commit()
      



