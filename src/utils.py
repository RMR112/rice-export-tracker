def custom_date_input(label, default_date=None, key=None):
    import streamlit as st
    from datetime import datetime

    st.write(f"📅 {label}")
    date_str = st.text_input(
        label=label,
        value=default_date.strftime("%d/%m/%Y") if default_date else "",
        key=key,
        label_visibility="collapsed"  # hides label, avoids warning
    )

    try:
        date_obj = datetime.strptime(date_str, "%d/%m/%Y").date()
        return date_obj
    except ValueError:
        st.warning("⚠️ Please enter a valid date in DD/MM/YYYY format.")
        return None
