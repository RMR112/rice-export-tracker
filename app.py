# app.py
import streamlit as st
from src.db import init_db, insert_order, get_all_orders, insert_shipment, get_shipments,get_unassigned_orders,assign_orders_to_shipment
from src.models import Order, Shipment
import pandas as pd
from src.utils import custom_date_input
from datetime import date

# Initialize DB
init_db()

# Streamlit UI
st.set_page_config(page_title="Rice Export Tracker", layout="wide")
st.title("📦 Rice Export Order Tracker")

# Sidebar Navigation
st.sidebar.title("Menu")
menu_option = st.sidebar.radio("Navigate", ["Add Order", "View Orders", "Track Shipments"])
# Add Order Section
if menu_option == "Add Order":
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
#View Order Section
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
# Track Shipments Section
elif menu_option == "Track Shipments":
    st.subheader("🚢 Manage Shipments")

    # Form to add new shipment
    with st.form("shipment_form"):
        container_id = st.text_input("Container ID")
        vessel_name = st.text_input("Vessel Name")
        departure_date = st.date_input("Departure Date")
        status = st.selectbox("Current Status", ["Dispatched", "In Transit", "Customs Cleared", "Delivered"])
        notes = st.text_area("Notes (optional)")
        submitted = st.form_submit_button("Save Shipment")

        if submitted:
            shipment = Shipment(container_id, vessel_name, departure_date.strftime("%d/%m/%Y"), status, notes)
            insert_shipment(shipment)
            st.success(f"Shipment {container_id} added.")

    # Display existing shipments
    st.divider()
    st.subheader("📋 All Shipments")

    shipments = get_shipments()

    if shipments:
        df = pd.DataFrame(shipments, columns=[
            "ID", "Container ID", "Vessel Name", "Departure Date", "Status", "Notes"
        ])


        # Display with status as colored badges
        def style_status(row):
            status = row["Status"]
            color = {
                "Dispatched": "gray",
                "In Transit": "blue",
                "Customs Cleared": "orange",
                "Delivered": "green"
            }.get(status, "black")
            return f'<span style="color:white;background-color:{color};padding:2px 8px;border-radius:6px;">{status}</span>'


        df["Status"] = df.apply(style_status, axis=1)

        st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.info("No shipments available yet.")

    st.divider()
    st.subheader("📦 Assign Orders to Shipment")

    # 1. Select a shipment
    shipment_options = shipments
    shipment_dict = {f"{cid} (ID: {sid})": sid for sid, cid, *_ in shipment_options}
    selected_shipment_label = st.selectbox("Select Shipment", list(shipment_dict.keys()))

    if selected_shipment_label:
        selected_shipment_id = shipment_dict[selected_shipment_label]

        # 2. Show unassigned orders
        unassigned_orders = get_unassigned_orders()
        if unassigned_orders:
            order_display = [f"{oid} - {buyer} ({variety}, {qty} MT)" for oid, buyer, variety, qty in unassigned_orders]
            order_id_map = {display: oid for display, (oid, *_rest) in zip(order_display, unassigned_orders)}

            selected_order_labels = st.multiselect("Select Orders to Assign", order_display)

            if st.button("Assign Selected Orders"):
                selected_order_ids = [order_id_map[label] for label in selected_order_labels]
                assign_orders_to_shipment(selected_shipment_id, selected_order_ids)
                st.success(f"✅ Assigned {len(selected_order_ids)} order(s) to shipment {selected_shipment_label}")

        else:
            st.info("All orders are already assigned to shipments.")
