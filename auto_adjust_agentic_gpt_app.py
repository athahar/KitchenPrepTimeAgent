
import streamlit as st
import random
from datetime import datetime
import openai
import os

st.set_page_config(page_title="AutoAdjustPrepTime Agent", layout="wide")

# Get API Key (replace with your secret in Streamlit Cloud)
openai.api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else os.getenv("OPENAI_API_KEY")

# Initialize session state
if "orders" not in st.session_state:
    st.session_state.orders = []
if "staff_percent" not in st.session_state:
    st.session_state.staff_percent = 100
if "base_prep_time" not in st.session_state:
    st.session_state.base_prep_time = 35
if "agent_logs" not in st.session_state:
    st.session_state.agent_logs = []
if "gpt_summary" not in st.session_state:
    st.session_state.gpt_summary = ""

# Agent decision logic
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

    staff_mod = {
        50: 1.5,
        75: 1.2,
        100: 1.0,
        125: 0.8
    }

    adj_factor = staff_mod.get(staff_level, 1.0)
    final_time = base_time + int(load_adj * adj_factor)
    reason = f"{n} active orders with {staff_level}% staff resulted in +{int(load_adj * adj_factor)} min adjustment."
    return final_time, reason

# Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Simulator", "Kitchen Display System", "Agent Summary"])

# Page 1: Dashboard
if page == "Dashboard":
    st.title("📊 Dashboard - AutoAdjustPrepTime Agent")

    prep_time, reason = adjust_prep_time(st.session_state.orders, st.session_state.staff_percent)
    st.metric("Total Active Orders", len(st.session_state.orders))
    st.metric("Staff Availability", f"{st.session_state.staff_percent}%")
    st.metric("Current Prep Time", f"{prep_time} minutes")

    if st.session_state.agent_logs == [] or st.session_state.agent_logs[-1]["prep_time"] != prep_time:
        st.session_state.agent_logs.append({
            "timestamp": datetime.now().isoformat(),
            "orders": len(st.session_state.orders),
            "staff_percent": st.session_state.staff_percent,
            "prep_time": prep_time,
            "reason": reason
        })

# Page 2: Simulator
elif page == "Simulator":
    st.title("🧪 Order Load & Staffing Simulator")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Add 5 Orders"):
            for _ in range(5):
                st.session_state.orders.append({
                    "id": f"O{random.randint(1000, 9999)}",
                    "source": random.choice(["dine_in", "online", "ubereats", "doordash"]),
                    "num_items": random.randint(1, 6),
                    "timestamp": datetime.now()
                })
    with col2:
        if st.button("Clear Orders"):
            st.session_state.orders = []

    st.subheader("Set Staff Availability")
    st.session_state.staff_percent = st.slider("Staff %", 50, 125, st.session_state.staff_percent, step=25)

# Page 3: Kitchen Display System
elif page == "Kitchen Display System":
    st.title("👨‍🍳 Kitchen Display System (KDS)")

    if not st.session_state.orders:
        st.info("No active orders. Go to the Simulator to add orders.")
    else:
        cols = st.columns(4)
        for idx, order in enumerate(st.session_state.orders[:8]):
            with cols[idx % 4]:
                st.markdown(f"**Order {order['id']}**")
                for i in range(order['num_items']):
                    st.write(f"• Item {i+1}")
                st.caption(order['source'].upper())
                if st.button(f"✅ Complete {order['id']}", key=order['id']):
                    st.session_state.orders = [o for o in st.session_state.orders if o['id'] != order['id']]

# Page 4: Agent Summary
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
            st.error(f"Failed to call OpenAI: {e}")

    if st.session_state.gpt_summary:
        st.subheader("🔍 GPT Summary")
        st.write(st.session_state.gpt_summary)

    if st.session_state.agent_logs:
        st.subheader("📝 Recent Agent Logs")
        for log in st.session_state.agent_logs[-5:]:
            st.write(f"🕒 **{log['timestamp']}**: {log['reason']} ➡️ Prep Time: **{log['prep_time']} mins**")
    else:
        st.info("No decisions made yet. Add orders and revisit dashboard.")
