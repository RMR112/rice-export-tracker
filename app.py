# app.py
import streamlit as st
from src.db import init_db, insert_order, get_all_orders
from src.models import Order
import pandas as pd

# Initialize DB
init_db()

# Streamlit UI
st.set_page_config(page_title="Rice Export Tracker", layout="wide")
st.title("📦 Rice Export Order Tracker")

# Sidebar Navigation
st.sidebar.title("Menu")
menu_option = st.sidebar.radio("Navigate", ["Add Order", "View Orders"])

if menu_option == "Add Order":
    st.subheader("➕ Add New Export Order")

    with st.form("order_form"):
        buyer = st.text_input("Buyer Name")
        country = st.selectbox("Destination Country", ["USA", "UK", "Canada", "Other"])
        variety = st.text_input("Rice Variety")
        quantity_mt = st.number_input("Quantity (in MT)", min_value=0.0)
        price_per_mt = st.number_input("Price per MT", min_value=0.0)
        order_date = st.date_input("Order Date")
        expected_ship_date = st.date_input("Expected Shipping Date")
        notes = st.text_area("Notes (optional)")
        submitted = st.form_submit_button("Save Order")

        if submitted:
            order = Order(buyer, country, variety, quantity_mt, price_per_mt, str(order_date), str(expected_ship_date), notes)
            insert_order(order)
            st.success(f"Order saved for {buyer} ({country})")

elif menu_option == "View Orders":
    st.subheader("📋 All Orders")

    orders = get_all_orders()
    if orders:
        df = pd.DataFrame(orders, columns=[
            "ID", "Buyer", "Country", "Variety", "Quantity (MT)",
            "Price/MT", "Order Date", "Expected Ship Date", "Notes"
        ])
        st.dataframe(df)
    else:
        st.info("No orders found.")
