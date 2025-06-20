import streamlit as st
import pandas as pd
from datetime import date
from src.models import Order
from src.db import insert_order, get_all_orders


def add_order_ui():
    st.subheader("➕ Add New Export Order")
    with st.form("order_form"):
        buyer = st.text_input("Buyer Name")
        country = st.selectbox("Destination Country", ["USA", "UK", "Canada", "Other"])
        variety = st.text_input("Rice Variety")
        quantity_mt = st.number_input("Quantity (in MT)", min_value=0.0)
        price_per_mt = st.number_input("Price per MT", min_value=0.0)
        # order_date = custom_date_input("Order Date", default_date=date.today(), key="order_date_input")
        order_date = st.date_input("Order Date")
        # expected_ship_date = custom_date_input("Expected Shipping Date", default_date=date.today(), key="ship_date_input")
        expected_ship_date = st.date_input("Expected Shipping Date")
        notes = st.text_area("Notes (optional)")
        submitted = st.form_submit_button("Save Order")

        if submitted:
            if expected_ship_date < order_date:
                st.error("🚫 Expected Shipping Date cannot be before the Order Date.")
            else:
                formatted_order_date = order_date.strftime("%d/%m/%Y")
                formatted_ship_date = expected_ship_date.strftime("%d/%m/%Y")

                # Show captions after submission
                st.caption(f"📅 Selected Order Date: **{formatted_order_date}**")
                st.caption(f"🚢 Expected Ship Date: **{formatted_ship_date}**")
                # Save order
                order = Order(buyer, country, variety, quantity_mt, price_per_mt,
                              formatted_order_date, formatted_ship_date, notes)
                insert_order(order)
                st.success(f"Order saved for {buyer} ({country})")

def view_orders_ui():
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