
import streamlit as st
import random
from datetime import datetime

st.set_page_config(page_title="AutoAdjustPrepTime Agent", layout="wide")

# Initialize session state
if "orders" not in st.session_state:
    st.session_state.orders = []
if "staff_percent" not in st.session_state:
    st.session_state.staff_percent = 100
if "base_prep_time" not in st.session_state:
    st.session_state.base_prep_time = 35
if "last_prep_time" not in st.session_state:
    st.session_state.last_prep_time = 35
if "agent_logs" not in st.session_state:
    st.session_state.agent_logs = []
if "gpt_summary" not in st.session_state:
    st.session_state.gpt_summary = ""

# Agent logic
def adjust_prep_time(orders, staff_level, base_time=35):
    n = len(orders)
    if n < 15:
        load_adj = 0
    elif 15 <= n < 25:
        load_adj = 10
    elif 25 <= n < 35:
        load_adj = 20
    else:
        load_adj = 30

    staff_mod = {50: 1.5, 75: 1.2, 100: 1.0, 125: 0.8}
    adj_factor = staff_mod.get(staff_level, 1.0)
    final_time = base_time + int(load_adj * adj_factor)
    reason = f"{n} active orders with {staff_level}% staff resulted in +{int(load_adj * adj_factor)} min adjustment."
    return final_time, reason

def add_orders(source, count):
    for _ in range(count):
        st.session_state.orders.append({
            "id": f"O{random.randint(1000, 9999)}",
            "source": source,
            "num_items": random.randint(1, 5),
            "timestamp": datetime.now()
        })

def display_toast_if_changed(current_prep):
    if current_prep != st.session_state.last_prep_time:
        delta = current_prep - st.session_state.last_prep_time
        direction = "⬆️" if delta > 0 else "⬇️"
        st.toast(f"{direction} Prep Time {'increased' if delta > 0 else 'decreased'} to {current_prep} minutes")
        st.session_state.last_prep_time = current_prep

# Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Kitchen Monitor", "Kitchen Display"])

# Shared calculation
prep_time, reason = adjust_prep_time(st.session_state.orders, st.session_state.staff_percent)
display_toast_if_changed(prep_time)

# Kitchen Monitor Page (Dashboard + Controls)
if page == "Kitchen Monitor":
    st.title("🍳 Kitchen Monitor")

    # Summary
    st.subheader("Current Load")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Orders", len(st.session_state.orders))
    with col2:
        st.metric("Staff Availability", f"{st.session_state.staff_percent}%")
    with col3:
        st.metric("Prep Time", f"{prep_time} min")

    st.subheader("Add Orders")
    c1, c2, c3, c4 = st.columns(4)
    if c1.button("+5 Dine-in"):
        add_orders("dine_in", 5)
    if c2.button("+5 Online"):
        add_orders("online", 5)
    if c3.button("+5 UberEats"):
        add_orders("ubereats", 5)
    if c4.button("+5 DoorDash"):
        add_orders("doordash", 5)

    st.subheader("Staffing")
    st.session_state.staff_percent = st.slider("Kitchen Staff %", 50, 125, st.session_state.staff_percent, step=25)

# KDS Page
elif page == "Kitchen Display":
    st.title("👨‍🍳 Kitchen Display System (KDS)")

    if not st.session_state.orders:
        st.info("No active orders.")
    else:
        cols = st.columns(4)
        for idx, order in enumerate(st.session_state.orders[:12]):
            with cols[idx % 4]:
                st.markdown(f"**Order {order['id']}**")
                for i in range(order['num_items']):
                    st.write(f"• Item {i+1}")
                st.caption(order['source'].upper())
                if st.button(f"✅ Complete {order['id']}", key=order['id']):
                    st.session_state.orders = [o for o in st.session_state.orders if o['id'] != order['id']]
