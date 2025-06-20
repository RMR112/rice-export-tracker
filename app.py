# app.py
import streamlit as st
from src.db import init_db
from src.orders import add_order_ui, view_orders_ui
from src.shipments import manage_shipments_ui, assign_orders_ui

# Initialize
init_db()
st.set_page_config(page_title="Rice Export Tracker", layout="wide")
st.title("📦 Rice Export Order Tracker")

# Sidebar
st.sidebar.title("📊 Export Tracker")
menu_option = st.sidebar.radio("Navigate", [
    "Add Order", "View Orders", "Track Shipments", "Assign Orders to Shipment"
])

# Routing
if menu_option == "Add Order":
    add_order_ui()
elif menu_option == "View Orders":
    view_orders_ui()
elif menu_option == "Track Shipments":
    manage_shipments_ui()
elif menu_option == "Assign Orders to Shipment":
    assign_orders_ui()
