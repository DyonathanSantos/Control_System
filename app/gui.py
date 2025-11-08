import streamlit as st
import pandas as pd
from crud import *
import matplotlib.pyplot as plt
import os, shutil, datetime

st.set_page_config(page_title="Bar & Adega System", page_icon="🍻", layout="wide")

# -------------------------
# SESSION CONTROL
# -------------------------
if "user" not in st.session_state:
    st.session_state["user"] = None
if "role" not in st.session_state:
    st.session_state["role"] = None

# -------------------------
# LOGIN PAGE
# -------------------------
if st.session_state["user"] is None:
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    role = st.text_input("role")

    if st.button("Login"):
        user = login_user(username, password)
        if user:
            st.session_state["user"] = user[1]
            st.session_state["role"] = user[3]
            st.success(f"✅ Welcome, {user[1]}! Role: {user[3]}")
            st.rerun()
        else:
            st.error("❌ Incorrect username or password.")
            st.stop()
    if st.button("Register Login"):
        user = register_user(username, password, role)
        if user:
            st.success(f"✅ Registered, make login, please")
            st.rerun()
        else:
            st.error("❌ Enter your username and password to register")
    st.stop()

    # -------------------------
# SIDEBAR MENU
# -------------------------
st.sidebar.title("🍺 Bar & Adega Control")
st.sidebar.write(f"👤 Logged as: **{st.session_state['user']} ({st.session_state['role']})**")
menu = st.sidebar.radio(
    "Choose an option:",
    ["🏠 Home","💸 Sale", "🧾 Comandas", "📦 Stock", "👤 Users", "📊 Reports","⚙️ Configuration","🚪 Logout"]
)

# -------------------------
# LOGOUT OPTION
# -------------------------
if menu == "🚪 Logout":
    st.session_state["user"] = None
    st.session_state["role"] = None
    st.rerun()

# -------------------------
# HOME
# -------------------------
if menu == "🏠 Home":
    st.title("🍻 Welcome to Bar & Adega System")
    st.info("Use the sidebar to navigate. Your permissions depend on your role (admin/user).")

# -------------------------
# STOCK (ADMIN ONLY)
# -------------------------
elif menu == "📦 Stock":
    if st.session_state["role"] != "admin":
        st.warning("⚠️ Only admins can access this section.")
    else:
        st.title("📦 Product Stock")

    if "selected_action" not in st.session_state:
        st.session_state.selected_action = None

    col1, col2 = st.columns(2)
    with col1:
        action = st.selectbox("Action", ["New Product","Update Stock","Delete Product"])

        if st.button("Select"):
                st.session_state.selected_action = action  # store user choice
            
        if st.session_state.selected_action == "New Product":
            st.write("### ➕ Add Product")
            name = st.text_input("Product Name")
            category = st.selectbox("Category", ["Bebida Alcoólica", "Bebida Não Alcoólica", "Comida", "Outros"])
            quantity = st.number_input("Quantity", min_value=0)
            cost = st.number_input("Cost Price (R$)", min_value=0.0)
            price = st.number_input("Sale Price (R$)", min_value=0.0)

            if st.button("Add Product"):
                try:
                    add_product_stock(name,quantity, category, cost, price)
                    st.success(f"✅ Product '{name}' added successfully!")
                except Exception as e:
                    st.error(f'❌ Error for add new product: {e}')
        elif st.session_state.selected_action == "Update Stock":

            product = see_stock()
            if product is not None and not product.empty:

                product_dict = {f"{row['product']} (ID{row['id']})": row['id'] for _, row in product.iterrows()}
                name_product = st.selectbox("Select Product", list(product_dict.keys()))
                id_product = product_dict[name_product]
                quantity = st.number_input("Quantity", min_value= 1)

                if st.button("Confirm Update"):
                    try:
                        update_stock(id_product, quantity)
                        st.success(f"✅ {quantity}x {name_product} adicionados ao estoque")
                    except Exception as e:
                        st.error(f"❌ Error for add item in comanda {e}")
                else:
                    st.info('Adicione o produto caso não ache na seleção')

        # DELETE PRODUCT FROM STOCK
        elif st.session_state.selected_action == "Delete Product":
            product = see_stock()

            if product is not None and not product.empty:
                product_dict = {f"{row['product']} (ID{row['id']})": row['id'] for _, row in product.iterrows()}
                name_product = st.selectbox("Select product", list(product_dict.keys()))
                id_product = product_dict[name_product]

                if st.button('Confirm'):
                    try:
                        delete_stock(id_product)
                        st.success(f'✅ Product Deleted {name_product}')
                    except Exception as e:
                        st.error(f'❌ Error for delete product')

        with col2:
            st.write("### 📋 Current Stock")
            df = see_stock()
            if df is not None and not df.empty:
                st.dataframe(df)
            else:
                st.info("No products registered yet.")

#Register Sale
elif menu == "💸 Sale":
    st.title("💸 Individual sales")
    
    products = see_stock()
    try:
        if products is not None and not products.empty:

            product_dict = {f"{row['product']} (ID{row['id']})": (row['product'], row['sell']) for _, row in products.iterrows()}
            product_name = st.selectbox("Select product for sell", list(product_dict.keys()))
            product, price = product_dict[product_name]

            quantity = st.number_input('Quantity', min_value= 1)
            total = price * quantity
            st.write(f"#### 💳 **Total a pagar:** R$ {total:.2f}")

            if st.button("Confirm"):
                usuario = st.session_state.get("user")
                register_sale(product, quantity, price)
                register_log(usuario, f"Register individual sale, total {total:.2f}")
                st.success(f"✅ Venda registrada com sucesso! Total: R$ {total:.2f}")
    except Exception as e:
        st.error(f'Error for register sale {e}')
# -------------------------
# COMANDAS (All Users)
# -------------------------
elif menu == "🧾 Comandas":
    st.title("🧾 Manage Comandas")
    col1, col2 = st.columns(2)
    
    # Remember user selection
    if "selected_action" not in st.session_state:
        st.session_state.selected_action = None

    with col1:
        st.write("### 🧾 Close and Add items")
        action = st.selectbox("Action", ["Create Comanda","View Items","Close Comanda","Add item in comanda"])

        if st.button("Select"):
            st.session_state.selected_action = action  # store user choice

        if st.session_state.selected_action == "Close Comanda":
                comanda = see_comanda()

                if comanda is not None and not comanda.empty:
                    comanda_dict = {f"{row['customer']}(ID {row['id']})": row['id'] for _, row in comanda.iterrows()}
                    comanda_name = st.selectbox("Select Customer", list(comanda_dict.keys()))
                    comanda_id = comanda_dict[comanda_name]

                if st.button('Confirm'):
                    with connect() as con:
                        cur = con.cursor()
                        cur.execute("SELECT SUM(quantity * price) FROM item_comanda WHERE id_comanda = ?",(comanda_id,))
                        total = cur.fetchone() [0] or 0
                        close_comanda(comanda_id, st.session_state["user"])
                        st.success(f"✅ Comanda {comanda_id} closed! Total: R$ {total:.2f}")

        elif st.session_state.selected_action == "Create Comanda":
                name = st.text_input('Customer Name')
                if st.button('Confirm Create'):
                    add_comanda(name)
                    st.success(f"✅ Comanda Created {name}")
                else:
                    st.info('Waiting for customer name...')
        
        elif st.session_state.selected_action == "Add item in comanda":
            # Pegar todas as comandas abertas
            comanda = see_comanda()

            #Create a dictionary {name: id}
            if comanda is not None and not comanda.empty:
                comanda_dict = {f"{row['customer']} (ID {row['id']})": row['id'] for _, row in comanda.iterrows()}
                comanda_name = st.selectbox("Selecione a comanda",list(comanda_dict.keys()))
                id_comanda = comanda_dict[comanda_name]
            else:
                st.warning("⚠️ Nenhuma comanda aberta no momento.")
                st.stop()

            #Get products
            products = see_stock()

            # Create a dictionary
            if products is not None and not products.empty:
                product_dict = {f"{row['product']} (ID {row['id']})": row['id'] for _, row in products.iterrows()}
                name_product = st.selectbox('Select the product', list(product_dict.keys()))
                id_product = product_dict[name_product]
                quantity = st.number_input("Quantidade", min_value=1)

            if st.button("Confirmar Adição"):
                    try:
                        add_item_comanda(id_comanda, id_product, quantity)
                        st.success(f"✅ {quantity}x {name_product} adicionados à comanda {id_comanda}")
                    except Exception as e:
                        st.error(f"❌ Erro ao adicionar item: {e}")
            else:
                st.warning("⚠️ Nenhum produto disponível no estoque.")


        elif st.session_state.selected_action == "View Items":
            comanda = see_comanda()

            if comanda is not None and not comanda.empty:
                comanda_dict = {f"{row['customer']} (ID {row['id']})": row['id'] for _, row in comanda.iterrows()}
                comanda_name = st.selectbox("Selecione a comanda",list(comanda_dict.keys()))
                id_comanda = comanda_dict[comanda_name]
            else:
                st.warning("⚠️ Nenhuma comanda aberta no momento.")
                st.stop()

            if st.button(" View Item"):
                try:
                    df = see_item_comanda(id_comanda)
                    if df is not None and not df.empty:
                        st.dataframe(df)
                        st.metric("Total", f"R$ {df['total'].sum():.2f}")
                except Exception as e:
                        st.error(f"❌ Erro ao adicionar item: {e}")



    with col2:
        st.write('### 🧾 Current Comandas')
        df = see_comanda()

        if df is not None and not df.empty:
                st.dataframe(df)
        else:
            st.info("No products registered yet.")


# -------------------------
# USERS (ADMIN ONLY)
# -------------------------
elif menu == "👤 Users":
    if st.session_state["role"] != "admin":
        st.warning("⚠️ Only admins can manage users.")
    else:
        st.title("👤 User Management")
        col1,col2 = st.columns(2)
        
    # Remember user selection
    if "selected_action" not in st.session_state:
        st.session_state.selected_action = None    


    with col1:
        st.write("### User register")
        action = st.selectbox("Action", ["User register", "Delete User","Logs"])

        if st.button("Select"):
            st.session_state.selected_action = action
        
        if st.session_state.selected_action == "Register User":

            username = st.text_input("Username")
            password = st.text_input("Password", type= 'password')
            role = st.text_input("Role")

            if st.button("Register"):
                try:
                    register_user(username, password, role)
                    st.success("Registered User")
                except Exception as e:
                    st.error(f'Error for Register {e}')

        elif st.session_state.selected_action == "Delete User":
            user = see_user()
            if user is not None and not user.empty:

                user_dict = {f"{row['username']}": row['id'] for _, row in user.iterrows()}
                user_name = st.selectbox("Username for Delete", list(user_dict.keys()))
                id_user = user_dict[user_name]

                if st.button("Delete"):
                    try:
                        delete_user(id_user)
                        st.success(f'User {user_name} delete!')
                    except Exception as e:
                        st.error(f"Error for Delete the User {e}")
        
        elif st.session_state.selected_action == "Logs":
            st.write('Registers of Logs')
            df = see_logs()

            if df is not None and not df.empty:
                st.dataframe(df)

#Colunm 2 with list of Users
    with col2:
        st.write("### 👤 List of Users")
        df = see_user()

        if df is not None and not df.empty:
            st.dataframe(df)
        else:
            st.info("No Users")


# -------------------------
# USERS (ADMIN ONLY)
# -------------------------
elif menu == "📊 Reports":
    if st.session_state["role"] != "admin":
        st.warning("⚠️ Only admins can manage users.")
    else:
        st.title("📈 Reports Dashboard")
        #Set DF for working
        stock = see_stock()
        sale = see_saler()

## ===============================
# 📊 REPORTS MENU
# =============================== 

        # Create options for the user
        option = st.sidebar.selectbox(
            "Select Report",
            [
                "Total Sales per Product",
                "Total Stock (Quantity and Value)"
            ]
        )

        # ----------------------------
        # 1️⃣ Total Sales per Product
        # ----------------------------
        if option == "Total Sales per Product":
            st.subheader("💵 Total Sales per Product")

            df_grouped = sale.groupby("product", as_index=False)["total"].sum()

            fig, ax = plt.subplots()
            ax.bar(df_grouped["product"], df_grouped["total"], color="skyblue")
            ax.set_title("Total Sales per Product")
            ax.set_xlabel("Product")
            ax.set_ylabel("Total Value (R$)")
            plt.xticks(rotation=45, ha="right")

            st.pyplot(fig)
            st.dataframe(df_grouped)

        # ----------------------------
        # 2️⃣ Total Stock and Value
        # ----------------------------
        elif option == "Total Stock (Quantity and Value)":
            st.subheader("📦 Total Stock")

            total_items = stock["quantity"].sum()
            total_value = (stock["quantity"] * stock["sell"]).sum()

            st.metric("Total Quantity of Items", f"{total_items}")
            st.metric("Total Value of Stock (R$)", f"{total_value:,.2f}")

            fig, ax = plt.subplots()
            ax.bar(stock["product"], stock["quantity"], color="orange")
            ax.set_title("Stock Quantity by Product")
            ax.set_xlabel("Product")
            ax.set_ylabel("Quantity")
            plt.xticks(rotation=45, ha="right")

            st.pyplot(fig)
            st.dataframe(stock)



elif menu == "⚙️ Configuration":
    st.title("⚙️ Configurações do Sistema")

    # -------------------------------
    # 📤 Upload do banco de dados
    # -------------------------------
    st.subheader("📤 Restaurar Banco de Dados (Upload)")

    auto_backup()
    uploaded_db = st.file_uploader("Selecione o arquivo `.db` para restaurar", type=["db"])

    if uploaded_db is not None:
        with open("base_bar.db", "wb") as f:
            f.write(uploaded_db.read())
        st.success("✅ Banco de dados atualizado com sucesso!")
        st.info("Recarregue a página para aplicar as mudanças.")

    # -------------------------------
    # 💾 Download do banco de dados
    # -------------------------------
    st.subheader("💾 Backup do Banco de Dados Atual")

    if os.path.exists("base_bar.db"):
        with open("base_bar.db", "rb") as f:
            st.download_button(
                label="⬇️ Baixar banco de dados (backup)",
                data=f,
                file_name=f"base_bar_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.db",
                mime="application/octet-stream"
            )
    else:
        st.warning("⚠️ Nenhum banco de dados encontrado para backup.")

    # -------------------------------
    # 📊 Informações do Sistema
    # -------------------------------
    st.subheader("📊 Informações do Sistema")

    db_info = get_db_info()
    col1, col2 = st.columns(2)

    if db_info:
        with col1:
            st.write("**📁 Caminho:**", db_info["path"])
            st.write(f"**📏 Tamanho:** {db_info['size_kb']:.2f} KB")
        with col2:
            st.write("**🕒 Última modificação:**", db_info["last_modified"])
    else:
        st.warning("⚠️ Nenhum banco de dados encontrado.")

        # -------------------------------
        # 👤 Sessão do Usuário
        # -------------------------------
        st.divider()
        st.subheader("👤 Sessão Atual")

        user = st.session_state.get("user", "Usuário não logado")
        role = st.session_state.get("role", "N/A")
        st.write(f"**Usuário:** {user}")
        st.write(f"**Permissão:** {role}")
        st.write(f"**Data Atual:** {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

        st.info("💡 Dica: Faça o download do banco de dados antes de fechar o site.")