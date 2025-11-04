import streamlit as st
import pandas as pd
from crud import *


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
    ["🏠 Home", "🧾 Comandas", "📦 Stock", "👤 Users", "📊 Reports", "🚪 Logout"]
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
                comanda_id = st.number_input('ID Comanda', min_value = 0)
                if st.button('Confirm'):
                    total = close_comanda(comanda_id, st.session_state["user"])
                    st.success(f"✅ Comanda {comanda_id} closed! Total: R$ {total}")

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
        st.write("### Register User")
        action = st.selectbox("Action", ["Register User", "Delete User"])

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
        st.title("📊 Reports/Logs")
        col1,col2 = st.columns(2)
        
    # Remember user selection
    if "selected_action" not in st.session_state:
        st.session_state.selected_action = None

    with col1:
        st.write('### 💰 Sales')

        df = see_saler()

        if df is not None and not df.empty:
            st.dataframe(df)
