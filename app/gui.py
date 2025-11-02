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

        col1, col2 = st.columns(2)
        with col1:
            st.write("### ➕ Add Product")
            name = st.text_input("Product Name")
            category = st.selectbox("Category", ["Bebida Alcoólica", "Bebida Não Alcoólica", "Comida", "Outros"])
            quantity = st.number_input("Quantity", min_value=0)
            cost = st.number_input("Cost Price (R$)", min_value=0.0)
            price = st.number_input("Sale Price (R$)", min_value=0.0)

            if st.button("Add Product"):
                add_product_stock(name,quantity, category, cost, price)
                st.success(f"✅ Product '{name}' added successfully!")

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
        
        elif st.session_state.selected_action = "Add item in comanda":
            comanda_id = 
                

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
        st.write("Here you can create new users (feature coming soon).")