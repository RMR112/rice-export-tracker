import streamlit as st
import pandas as pd
from src.models import Shipment
from src.db import (
    insert_shipment, get_shipments,
    get_unassigned_orders, assign_orders_to_shipment,get_orders_by_shipment
)

def manage_shipments_ui():
    st.subheader("📋 All Shipments")
    shipments = get_shipments()
    if shipments:
        df = pd.DataFrame(shipments, columns=[
            "ID", "Container ID", "Vessel Name", "Departure Date", "Status", "Notes"
        ])
        df["Status"] = df.apply(lambda row: format_status_badge(row["Status"]), axis=1)
        st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.info("No shipments available yet.")

    st.divider()
    st.subheader("🚢 Manage Shipments")

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


def assign_orders_ui():
    st.subheader("📦 Assign Orders to Shipment")

    shipment_options = get_shipments()
    shipment_dict = {f"{cid} (ID: {sid})": sid for sid, cid, *_ in shipment_options}
    selected_shipment_label = st.selectbox("Select Shipment", list(shipment_dict.keys()))

    if selected_shipment_label:
        selected_shipment_id = shipment_dict[selected_shipment_label]
        # ✅ 1. Show assigned orders to this shipment
        assigned_orders = get_orders_by_shipment(selected_shipment_id)
        if assigned_orders:
            st.markdown("### 🧾 Orders Assigned to this Shipment")
            df_assigned = pd.DataFrame(assigned_orders, columns=["Order ID", "Buyer", "Variety", "Quantity (MT)"])
            st.dataframe(df_assigned, use_container_width=True)
        else:
            st.info("No orders assigned to this shipment yet.")

        st.divider()
        # ✅ 2. Assign new orders
        unassigned_orders = get_unassigned_orders()

        if unassigned_orders:
            st.markdown("### ➕ Assign More Orders to Shipment")
            order_display = [
                f"{oid} - {buyer} ({variety}, {qty} MT)"
                for oid, buyer, variety, qty in unassigned_orders
            ]
            order_id_map = {display: oid for display, (oid, *_rest) in zip(order_display, unassigned_orders)}

            selected_order_labels = st.multiselect("Select Orders to Assign", order_display)

            if st.button("Assign Selected Orders"):
                selected_order_ids = [order_id_map[label] for label in selected_order_labels]
                assign_orders_to_shipment(selected_shipment_id, selected_order_ids)
                st.success(f"✅ Assigned {len(selected_order_ids)} order(s) to shipment {selected_shipment_label}")
        else:
            st.info("All orders are already assigned to shipments.")

def format_status_badge(status):
    color = {
        "Dispatched": "gray",
        "In Transit": "blue",
        "Customs Cleared": "orange",
        "Delivered": "green"
    }.get(status, "black")
    return f'<span style="color:white;background-color:{color};padding:2px 8px;border-radius:6px;">{status}</span>'

