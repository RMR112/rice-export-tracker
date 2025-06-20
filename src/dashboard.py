import streamlit as st
import pandas as pd
from src.db import get_all_orders, get_shipments

def dashboard_ui():
    st.subheader("📊 Dashboard Overview")

    # Load data
    orders = get_all_orders()
    shipments = get_shipments()

    # Convert to DataFrame
    orders_df = pd.DataFrame(orders, columns=[
        "ID", "Buyer", "Country", "Variety", "Quantity (MT)",
        "Price/MT", "Order Date", "Expected Ship Date", "Notes"
    ]) if orders else pd.DataFrame()

    shipments_df = pd.DataFrame(shipments, columns=[
        "ID", "Container ID", "Vessel Name", "Departure Date", "Status", "Notes"
    ]) if shipments else pd.DataFrame()

    # --- KPIs ---
    st.markdown("### 📦 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Orders", len(orders_df))
    col2.metric("Total Shipments", len(shipments_df))
    col3.metric("Pending Orders", get_pending_order_count(orders_df, shipments_df))
    col4.metric("Delivered Shipments", len(shipments_df[shipments_df["Status"] == "Delivered"]))

    st.divider()

    # --- Orders by Country ---
    if not orders_df.empty:
        st.markdown("### 🌍 Orders by Destination Country")
        country_summary = orders_df.groupby("Country")["Quantity (MT)"].sum().reset_index()
        st.bar_chart(country_summary.set_index("Country"))

    # --- Shipment Status Distribution ---
    if not shipments_df.empty:
        st.markdown("### 🚢 Shipment Status Distribution")
        status_summary = shipments_df["Status"].value_counts().reset_index()
        status_summary.columns = ["Status", "Count"]
        st.bar_chart(status_summary.set_index("Status"))

    st.divider()

    # --- Recent Orders ---
    if not orders_df.empty:
        st.markdown("### 🕒 Recent Orders")
        st.dataframe(orders_df.sort_values("ID", ascending=False).head(5))

    # --- Recent Shipments ---
    if not shipments_df.empty:
        st.markdown("### 🕒 Recent Shipments")
        st.dataframe(shipments_df.sort_values("ID", ascending=False).head(5))


# Utility to compute pending orders
def get_pending_order_count(orders_df, shipments_df):
    # Get all assigned order IDs
    from src.db import get_all_assigned_order_ids
    assigned_ids = get_all_assigned_order_ids()
    if assigned_ids:
        return len(orders_df[~orders_df["ID"].isin(assigned_ids)])
    return len(orders_df)
