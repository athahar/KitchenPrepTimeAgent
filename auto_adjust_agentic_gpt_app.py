
import streamlit as st
import random
from datetime import datetime

st.set_page_config(page_title="AutoAdjustPrepTime Agent", layout="wide")

st.markdown("""<style>
.order-card {
    border: 2px solid #ccc;
    border-radius: 10px;
    padding: 1rem;
    margin-bottom: 1rem;
    background-color: #f9f9f9;
    box-shadow: 2px 2px 8px rgba(0,0,0,0.05);
}
.order-header {
    font-weight: bold;
    font-size: 1.1rem;
    margin-bottom: 0.5rem;
}
.item-list {
    margin-bottom: 0.5rem;
}
.source-badge {
    font-size: 0.75rem;
    color: #666;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
    display: block;
}
.order-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
}
</style>""", unsafe_allow_html=True)

# Session state setup
if "orders" not in st.session_state:
    st.session_state.orders = []

# Page Title
st.title("👨‍🍳 Kitchen Display System (KDS)")

# Add sample orders if empty
if not st.session_state.orders:
    for _ in range(10):
        st.session_state.orders.append({
            "id": f"O{random.randint(1000, 9999)}",
            "source": random.choice(["dine_in", "online", "ubereats", "doordash"]),
            "num_items": random.randint(2, 5),
            "timestamp": datetime.now()
        })

# Render Orders in Grid
st.markdown('<div class="order-grid">', unsafe_allow_html=True)

for order in st.session_state.orders:
    order_html = f'''
    <div class="order-card">
        <div class="order-header">Order {order["id"]}</div>
        <div class="item-list">
            {"<br>".join([f"• Item {i+1}" for i in range(order["num_items"])])}
        </div>
        <span class="source-badge">{order["source"].upper()}</span>
    </div>
    '''
    st.markdown(order_html, unsafe_allow_html=True)
    if st.button(f"✅ Complete {order['id']}", key=order['id']):
        st.session_state.orders = [o for o in st.session_state.orders if o['id'] != order['id']]

st.markdown('</div>', unsafe_allow_html=True)
