
import streamlit as st
import random
from datetime import datetime
import openai
import os

st.set_page_config(page_title="AutoAdjustPrepTime Agent", layout="wide")

# Setup secrets for GPT
openai.api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else os.getenv("OPENAI_API_KEY")

# Session state
if "orders" not in st.session_state:
    st.session_state.orders = []
if "completed_orders" not in st.session_state:
    st.session_state.completed_orders = []
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

# Style block
st.markdown("""<style>
.order-card {
    border: 2px solid #ccc;
    border-radius: 10px;
    padding: 1rem;
    margin: 0.5rem;
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
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    justify-content: flex-start;
}
.order-wrapper {
    flex: 0 1 calc(25% - 1rem);
    box-sizing: border-box;
}
@media (max-width: 1024px) {
    .order-wrapper {
        flex: 0 1 calc(50% - 1rem);
    }
}
@media (max-width: 640px) {
    .order-wrapper {
        flex: 0 1 100%;
    }
}
</style>""", unsafe_allow_html=True)

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
page = st.sidebar.radio("Go to", ["Kitchen Monitor", "Kitchen Display", "Agent Summary"])

# Prep time decision
prep_time, reason = adjust_prep_time(st.session_state.orders, st.session_state.staff_percent)
display_toast_if_changed(prep_time)

if st.session_state.agent_logs == [] or st.session_state.agent_logs[-1]["prep_time"] != prep_time:
    st.session_state.agent_logs.append({
        "timestamp": datetime.now().isoformat(),
        "orders": len(st.session_state.orders),
        "staff_percent": st.session_state.staff_percent,
        "prep_time": prep_time,
        "reason": reason
    })

# Dashboard + Simulator
if page == "Kitchen Monitor":
    st.title("🍳 Kitchen Monitor")
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
        st.rerun()
    if c2.button("+5 Online"):
        add_orders("online", 5)
        st.rerun()
    if c3.button("+5 UberEats"):
        add_orders("ubereats", 5)
        st.rerun()
    if c4.button("+5 DoorDash"):
        add_orders("doordash", 5)
        st.rerun()

    st.subheader("Staffing")
    st.session_state.staff_percent = st.slider("Kitchen Staff %", 50, 125, st.session_state.staff_percent, step=25)

# KDS Page
elif page == "Kitchen Display":
    st.title("👨‍🍳 Kitchen Display System (KDS)")
    st.markdown('<div class="order-grid">', unsafe_allow_html=True)

    new_active_orders = []
    for order in st.session_state.orders:
        st.markdown('<div class="order-wrapper">', unsafe_allow_html=True)
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
            st.session_state.completed_orders.insert(0, order)
        else:
            new_active_orders.append(order)
        st.markdown('</div>', unsafe_allow_html=True)
    st.session_state.orders = new_active_orders
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.completed_orders:
        st.subheader("🗂️ Recently Completed Orders")
        st.markdown('<div class="order-grid">', unsafe_allow_html=True)
        for order in st.session_state.completed_orders[:6]:
            st.markdown('<div class="order-wrapper">', unsafe_allow_html=True)
            html = f'''
            <div class="order-card" style="background-color:#e0f7e9;">
                <div class="order-header">Order {order["id"]}</div>
                <div class="item-list">
                    {"<br>".join([f"• Item {i+1}" for i in range(order["num_items"])])}
                </div>
                <span class="source-badge">{order["source"].upper()}</span>
            </div>
            '''
            st.markdown(html, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Agent Summary Page
elif page == "Agent Summary":
    st.title("🧠 Agent Session Summary")

    if st.button("🧠 Generate GPT Summary"):
        logs = st.session_state.agent_logs[-10:]
        context = "\n".join(
            f"{l['timestamp']}: {l['orders']} orders, {l['staff_percent']}% staff -> {l['prep_time']} mins (Reason: {l['reason']})"
            for l in logs
        )
        prompt = f'''
You are an operations assistant AI summarizing the performance of a kitchen prep time adjustment agent.
Here is the session log of decisions:
{context}

Generate a 3-sentence summary explaining what happened, what the agent reacted to, and what you recommend improving.
'''
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4
            )
            st.session_state.gpt_summary = response.choices[0].message.content
        except Exception as e:
            st.error(f"OpenAI failed: {e}")

    if st.session_state.gpt_summary:
        st.subheader("🔍 GPT Summary")
        st.write(st.session_state.gpt_summary)

    if st.session_state.agent_logs:
        st.subheader("📋 Recent Agent Logs")
        for log in st.session_state.agent_logs[-5:]:
            st.write(f"🕒 **{log['timestamp']}**: {log['reason']} ➡️ Prep Time: **{log['prep_time']} mins**")
