# AutoAdjustPrepTime Agentic AI App

This Streamlit app simulates an intelligent prep time agent for restaurant kitchens. It:
- Simulates real-time kitchen load and staffing
- Adjusts prep time autonomously based on demand and availability
- Generates GPT-powered summaries of agent decisions

## 🚀 How to Deploy on Streamlit Cloud

1. Fork or upload this repo to GitHub
2. Go to [https://streamlit.io/cloud](https://streamlit.io/cloud) and create a new app
3. Point to your GitHub repo and select `auto_adjust_agentic_gpt_app_fixed.py` as the main file
4. In the Streamlit Cloud **Secrets Manager**, add:

```
OPENAI_API_KEY = "your-api-key"
```

5. Click **Deploy**

## 📦 Files

- `auto_adjust_agentic_gpt_app_fixed.py` – Main Streamlit app
- `requirements.txt` – Required Python packages
- `.streamlit/config.toml` – Streamlit layout settings

## 🧠 Powered by GPT-4