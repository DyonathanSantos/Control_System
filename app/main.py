#Importando sqlite3
import sqlite3
from datetime import datetime
import pandas as pd

# Conexão com banco de dados e criação do mesmo.

def conectar():
    return sqlite3.connect('bar.db')

# Adicionando as tabelas do banco de dados e criando o cursor.
con = conectar()
cur = con.cursor()


# TABELA DE ESTOQUE
cur.execute('CREATE TABLE IF NOT EXISTS estoque( id INTEGER PRIMARY KEY AUTOINCREMENT, produto TEXT NOT NULL, tipo TEXT NOT NULL, quantidade INTEGER  NOT NULL, preco REAL NOT NULL, preco_venda REAL NOT NULL)')
con.commit()

#TABELA DE COMANDAS
cur.execute('CREATE TABLE IF NOT EXISTS comanda( id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, produto TEXT NOT NULL, quantidade INTEGER NOT NULL, preco_venda REAL NOT NULL, data TEXT)')
con.commit()

#TABELA DE VENDAS
cur.execute('CREATE TABLE IF NOT EXISTS venda(id INTEGER PRIMARY KEY AUTOINCREMENT, qnt_vendas INTEGER NOT NULL, total_vendas REAL NOT NULL, data TEXT)')
con.commit()

#TABELA DE GASTOS
cur.execute('CREATE TABLE IF NOT EXISTS gastos(data TEXT NOT NULL, descricao TEXT, valor REAL NOT NULL)')
con.commit()

#FECHANDO A CONEXÃO
con.close()

#----------------------------------

# ESTABELECENDO CONEXÃO
con = sqlite3.connect('bar.db',check_same_thread=False)

#CURSOR OF SQLITE3
cursor = con.cursor()

#C = CREATE OF CRUD -------------------------------------------------------------------------------

def adicionar_estoque(produto, tipo, quantidade, preco, preco_venda): #check
    cursor.execute("INSERT INTO estoque (produto, tipo, quantidade, preco, preco_venda) VALUES (?, ?, ?, ?, ?)",(produto.lower(), tipo.lower(), quantidade, preco, preco_venda))
    con.commit()
    print(f"Produto '{produto}' adicionado com sucesso!")
    

def abrir_comanda (nome,data): #check

    data = datetime.now().strftime("%d-%m-%Y %H:%M")
    cursor.execute("INSERT INTO comandas (nome, data) VALUES (?, ?)",(nome.upper(),data))
    con.commit()
    comanda_id = cursor.lastrowid
    print(f"✅ Comanda {comanda_id} aberta para {nome}")
    
    return comanda_id

def criar_venda (produto,quantidade,preco,total,data):
    data  = datetime.now().strftime("%d-%m-%Y %H:%M")
    cursor.execute("INSERT INTO venda (produto,quantidade,preco,total,data) VALUES (?, ?, ?, ?, ?)",(produto.upper(),quantidade,preco,total,data,))
    con.commit()
    print(f"Venda de {produto} adicionada com sucesso!")

#R = READ OF CRUD -------------------------------------------------------------------------------

def ver_estoque(): #check
    cursor.execute("SELECT * FROM estoque")
    rows = cursor.fetchall()

    if not rows:
        return pd.DataFrame()

    else:
        df = pd.DataFrame(rows,columns=["ID","produto","Tipo","Quantidade","Preco","Preco_venda"])
        return df

    



def listar_comandas_abertas(): #check
    cursor.execute("SELECT id,nome, status, data FROM comandas WHERE status = 'aberta'")
    comandas = cursor.fetchall()

    if not comandas:
        return pd.DataFrame()
    df = pd.DataFrame(comandas,columns=["ID","Nome","Status","Data"])
    return df

    
#LISTAR ITENS DE UMA COMANDA ESPECÍFICA

def listar_itens_comanda(id_comanda): #check
    cursor.execute("SELECT produto, quantidade, preco FROM comanda_itens WHERE id_comanda = ?",(id_comanda,))
    itens = cursor.fetchall()

    if not itens:
        return pd.DataFrame()
    else:
        df = pd.DataFrame(itens,columns=["Produto","Quantidade","Preço"])
        df['Total'] = df["Quantidade"]* df['Preço']
        return df
    
def vendas_see():
    cursor.execute("SELECT * FROM venda")
    vendas = cursor.fetchall()

    if not vendas:
       return pd.DataFrame()
    else:
        df = pd.DataFrame(vendas, columns=["ID","Produto","Quantidade","Preço","Total","Data"])
        return df    

# U = UPDATE OF CRUD -------------------------------------------------------------------------------------

#Atualizando estoque
def update_estoque(estoque_id, new_produto, new_tipo, new_qnd, new_preco, new_preco_venda): #check
    cursor.execute("UPDATE estoque SET produto = ?, tipo = ?, quantidade = ?, preco = ?, preco_venda = ? WHERE id = ?",(new_produto.lower(), new_tipo.lower(), new_qnd, new_preco, new_preco_venda, estoque_id))
    con.commit()
    print(f"Produto ID {estoque_id} Atualizado")

#ATUALIZANDO COMANDAS
def atualizar_comandas (id_comanda, produto, quantidade, preco): #CHECK

    cursor.execute("SELECT id, quantidade FROM comanda_itens WHERE id_comanda = ? AND produto = ?",(id_comanda, produto.lower()))
    item = cursor.fetchone()

    if item:
        novo_total = item[1] + quantidade
        cursor.execute("UPDATE comanda_itens SET quantidade = ? WHERE id = ?",(novo_total, item[0]))
        print(f"🔄 Atualizado: {produto} agora tem {novo_total} unidades na comanda {id_comanda}")
    else:
        cursor.execute("INSERT INTO comanda_itens (id_comanda, produto, quantidade, preco) VALUES(?, ?, ?, ?)",(id_comanda, produto.lower(), quantidade, preco))
        print(f"✅ Adicionado: {produto} x{quantidade} na comanda {id_comanda}")

    con.commit()

#FECHANDO COMANDAS
def fechar_comanda(id_comanda): #check
    data = datetime.now().strftime("%d-%m-%Y %H:%M")
    cursor.execute("SELECT produto, quantidade, preco FROM comanda_itens WHERE id_comanda = ?", (id_comanda,))
    itens = cursor.fetchall()

    for produto, quantidade, preco in itens:
        total = quantidade * preco
        cursor.execute("INSERT INTO venda (produto, quantidade, preco, total, data) VALUES (?, ?, ?, ?, ?)",(produto, quantidade, preco, total, data))
        cursor.execute("UPDATE estoque SET quantidade = quantidade - ? WHERE produto = ?",(quantidade, produto))
        cursor.execute("UPDATE comandas SET status = 'fechada' WHERE id = ? ",(id_comanda,))
        con.commit()
    print(f" ❌ Comanda com ID : {id_comanda} foi fechada!")




#D = DELETE OF CRUD ----------------------------------------------------------------------------------------------

def delete_estoque(estoque_id):  #check
    cursor.execute("DELETE FROM estoque WHERE id = ?",(estoque_id,))
    con.commit()
    print(f'Produto ID {estoque_id} deletado')
    

def comanda_clear(id_comanda): #check
    cursor.execute("DELETE FROM comanda_itens WHERE id_comanda = ?",(id_comanda,))
    con.commit()
    print("Itens limpados com sucesso e comanda apagada")

def comanda_delete(id_comanda): #check
    cursor.execute("DELETE FROM comandas WHERE id = ?",(id_comanda,))
    con.commit()
    print(f"comanda {id_comanda} apagada")
    

def vendas_clear_all():
    cursor.execute("DELETE FROM venda")
    con.commit()
    print("Vendas apagadas")
    

def vendas_clear_select(venda_id):
    cursor.execute("DELETE FROM venda WHERE id = ?",(venda_id,))
    con.commit()
    
#ARQUIVO PARA INTERFACE DO PROJETO 

#IMPORTAÇÃO DAS BIBLIOTECAS + O CRUD
from crud import *
import sqlite3
import pandas as pd
import streamlit as st

con = sqlite3.connect('bar.db')
cursor = con.cursor()



st.set_page_config(page_title="Bar & Adega", layout="wide")
st.title("🍺 Bar & Adega - Sistema de Controle")

# Menu lateral
menu = st.sidebar.radio("📌 Menu", ["Home","Cadastrar Produto no Estoque", "Vendas individuais","Listar Estoque","Nova Comanda", "Comandas","Adicionando Itens na comanda","Consultar comanda", "Fechando comanda","Apagar","Vendas",])

# ------------------------
# HOME
# ------------------------

if menu == "Home":
   st.markdown("""
    ## 🎉 Bem-vindo ao Sistema Bar & Adega

    Este sistema foi criado para facilitar o **gerenciamento do estoque, comandas e vendas** do bar.  
    Use o menu lateral para navegar entre as opções e manter tudo organizado.
    """)

    # --- Resumos ---
   col1, col2, col3 = st.columns(3)

    # Total de produtos no estoque
   df_estoque = ver_estoque()
   total_produtos = len(df_estoque) if not df_estoque.empty else 0

    # Total de comandas abertas
   df_comandas = listar_comandas_abertas()
   total_comandas = len(df_comandas) if not df_comandas.empty else 0

    # Total vendido (exemplo: soma do campo 'Total' das comandas fechadas)
   df_vendas = pd.read_sql_query("""
            SELECT SUM(total) as total_vendido
            FROM venda
        """,con)

   total_vendido = df_vendas["total_vendido"].iloc[0] if df_vendas["total_vendido"].iloc[0] else 0

    # Mostrar nos cards
   col1.metric("📦 Produtos no Estoque", total_produtos)
   col2.metric("🧾 Comandas Abertas", total_comandas)
   col3.metric("💰 Total Vendido", f"R$ {total_vendido:.2f}")

# ------------------------
# CADASTRAR
# ------------------------

if menu == "Cadastrar Produto no Estoque":

    st.subheader("Cadastrar novo produto no estoque")

    produto = st.text_input("Nome do Produto")
    tipo = st.text_input("Categoria")
    quantidade = st.number_input("Quantidade", min_value=1, step=1)
    preco = st.number_input("Preço de Compra", min_value=0.0, step=0.05)
    preco_venda = st.number_input("Preço de Venda", min_value=0.0, step=0.01)

    if st.button("Salvar Produto"):
        if produto and tipo and quantidade:
            adicionar_estoque(produto, tipo, quantidade, preco, preco_venda)
            st.success(f"✅ Produto '{produto}' cadastrado com sucesso!")
        else:
            st.error("❌ Preencha todos os campos antes de salvar.")

    if st.button("Atulizar estoque"):
       if produto and preco_venda and quantidade:
          update_estoque(produto,tipo, quantidade, preco, preco_venda)
          st.success(f"✅ Produto '{produto}' atualizado com sucesso!")
       else:
          st.error("❌ Preencha todos os campos antes de atualizar")

# ------------------------
# VENDAS INDIVIDUAIS
# ------------------------
elif menu == "Vendas individuais":
   st.subheader("Adicionar vendas sem comanda")

   produto = st.text_input("Produto")
   quantidade = st.number_input("Quantidade", min_value=0, step= 1)
   preco = st.number_input("Preço", min_value=0.00, step= 0.05)
   total = st.number_input("Preço total", min_value=0.0, step=0.05)
   data = st.text_input("Data")

   if st.button("Lançar venda"):  
    if produto and quantidade and preco:
        criar_venda(produto,quantidade,preco,total,data)
        st.success(f"Venda registrada com sucesso!")
    else:
        print("Por favor preencher os campos!")


# ------------------------
# LISTAR
# ------------------------
elif menu == "Listar Estoque":
    
    st.subheader("📋 Produtos Cadastrados")
    df = ver_estoque()

    if st.button("Ver estoque"):
        if df.empty:
            st.info("Nenhum produto cadastrado ainda.")
        else:
            st.dataframe(df)

# ------------------------
# CRIAR COMANDA
# ------------------------

elif menu == "Nova Comanda":
  
  st.subheader("Abrir comanda")

  nome = st.text_input("Nome do cliente")
  data = st.text_input('Data')

  if st.button("Criar Comanda"):
      if nome and data:
        abrir_comanda(nome,data)
        st.success(f"✅ Comanda criada com sucesso do cliente {nome}!")

      else:
          st.error("❌ Preencha todos os campos antes de criar a comanda.") 

# ------------------------
# COMANDA ABERTAS
# ------------------------

elif menu == "Comandas":
 
  st.subheader("Comandas Abertas")
  df = listar_comandas_abertas()

  if st.button('Ver comandas'):  
    if df.empty:
        st.info("Nenhuma comanda aberta ainda.")
    else:
        st.dataframe(df, use_container_width=True)


# ------------------------
# ADICIONANDO ITENS
# ------------------------

elif menu == "Adicionando Itens na comanda":
   
   st.subheader("Adicionar itens")

   id_comanda = st.number_input("ID do cliente", min_value=0, step=1)
   produto = st.text_input("Produto")
   quantidade = st.number_input("Quantidade",min_value= 0, step=1)
   preco = st.number_input("Preço",min_value=0.0, step= 0.05)

   if st.button("Adicionar"):
      if id_comanda and quantidade and produto:
         atualizar_comandas(id_comanda,produto,quantidade,preco)
         st.success(f"✅ Item {produto} adicionado com sucesso!")
      else:
          st.error("❌ Preencha todos os campos antes de criar a comanda.")

# ------------------------
# ITENS DE UMA COMANDA ESPECÍFICA
# ------------------------

elif menu == "Consultar comanda":
   
    st.subheader("Ver os itens da comanda de um cliente")
    id_comanda = st.number_input("Digite o ID da comanda do cliente que deseja ver os itens",min_value=0,step=1)

    if st.button("Listar itens"):
       df = listar_itens_comanda(id_comanda)

       if df.empty:
            st.warning(f"⚠️ Nenhum item encontrado na comanda {id_comanda}")
       else:
           st.subheader(f"🧾 Itens da Comanda {id_comanda}")
           st.dataframe(df)  # ou st.dataframe(df)
           st.metric("💰 Total da Comanda", f"R$ {df['Total'].sum():.2f}") 
        
    st.info("Para encontra o ID volte no menu Comandas e procure pelo nome do cliente, assim que achar terá um número a esquerda, este é o ID!")
    
        
# ------------------------
# FECHANDO COMANDA
# ------------------------

elif menu == "Fechando comanda":
   
   st.subheader("Fechar uma Comanda")
   id_comanda = st.number_input("Digite o ID", min_value= 0, step= 1)

   if st.button("FECHAR"):
      if id_comanda:
         fechar_comanda(id_comanda)
         st.success(f"Comanda de ID {id_comanda} foi fechada!")
      else:
         st.erro("Coloque o ID do cliente!!")


# ------------------------
# APAGAR
# ------------------------
elif menu == "Apagar":
   st.subheader("Concertar erros")

   id_number = st.number_input("Digite o ID", min_value= 0, step= 1)

   if st.button("Limpar um item do estoque"):
      delete_estoque(id_number)
      st.success(f"O item {id_number} apagado com sucesso!")
   elif st.button("Apagar item de comanda"):
      comanda_clear(id_number)
      st.success(f"O item {id_number} apagado com sucesso!")
   elif st.button("Excluir comanda"):
      comanda_delete(id_number)
      st.success(f"O item {id_number} apagado com sucesso!")
   elif  st.button('Excluir venda'):
      vendas_clear_select(id_number)
      st.success(f"O item {id_number} apagado com sucesso!")
   elif st.button('EXCLUIR VENDAS!!'):
      vendas_clear_all()
      st.success('VENDAS APAGADAS!')
      cursor.execute("DELETE FROM comandas WHERE status = 'fechada'")
      con.commit()
   else:
      st.error('COLOQUE O ID QUE DESEJA APAGAR!')  



# ------------------------
# VENDAS
# ------------------------
elif menu == "Vendas":
    st.subheader("📊 Vendas")

    df = vendas_see()
    if df.empty:
        st.info("Cadastre produtos para ver o resumo.")
    else:
       st.dataframe(df)

