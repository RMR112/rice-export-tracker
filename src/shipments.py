from datetime import datetime

import streamlit as st
import pandas as pd
from src.models import Shipment

from src.db import (
    insert_shipment, get_shipments,
    get_unassigned_orders, assign_orders_to_shipment,get_orders_by_shipment,update_shipment, get_shipment_by_id
)

def manage_shipments_ui():
    st.subheader("📋 All Shipments")

    shipments = get_shipments()

    if shipments:
        # Build radio button options with display text per row
        shipment_display = []
        shipment_id_map = {}

        for s in shipments:
            sid, cid, vessel, dep_date, status, notes = s
            display = f"🆔 {sid} | 📦 {cid} | 🚢 {vessel} | 📅 {dep_date} | 📍 {status} | 📝 {notes}"
            shipment_display.append(display)
            shipment_id_map[display] = sid

        selected_display = st.radio("Select a shipment to edit", shipment_display)
        selected_id = shipment_id_map[selected_display]

        if st.button("✏️ Edit Selected Shipment"):
            st.session_state.edit_shipment_id = selected_id

    else:
        st.info("No shipments available yet.")

    # --- Divider and Add Shipment Form ---
    st.divider()
    st.subheader("➕ Add New Shipment")

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


def edit_shipment_ui():
    shipment_id = st.session_state.get("edit_shipment_id", None)
    if shipment_id is None:
        st.warning("No shipment selected to edit.")
        return

    shipment = get_shipment_by_id(shipment_id)
    if not shipment:
        st.error("Shipment not found.")
        return

    sid, container_id, vessel_name, departure_date_str, status, notes = shipment
    departure_date = datetime.strptime(departure_date_str, "%d/%m/%Y").date()

    st.subheader(f"✏️ Edit Shipment - {container_id}")

    with st.form("edit_shipment_form"):
        container_id_input = st.text_input("Container ID", value=container_id)
        vessel_name_input = st.text_input("Vessel Name", value=vessel_name)
        departure_date_input = st.date_input("Departure Date", value=departure_date)
        status_input = st.selectbox("Current Status", ["Dispatched", "In Transit", "Customs Cleared", "Delivered"], index=["Dispatched", "In Transit", "Customs Cleared", "Delivered"].index(status))
        notes_input = st.text_area("Notes", value=notes)
        col1, col2 = st.columns(2)
        with col1:
            save = st.form_submit_button("💾 Save")
        with col2:
            cancel = st.form_submit_button("❌ Cancel")

    if save:
        updated = Shipment(container_id_input, vessel_name_input,
                           departure_date_input.strftime("%d/%m/%Y"),
                           status_input, notes_input)
        update_shipment(shipment_id, updated)
        st.success("Shipment updated successfully.")
        del st.session_state.edit_shipment_id

    if cancel:
        del st.session_state.edit_shipment_id
        st.info("Edit cancelled.")



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

