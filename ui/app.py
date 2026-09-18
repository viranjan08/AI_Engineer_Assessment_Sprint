import streamlit as st
import requests
import pandas as pd
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

# Must be the first Streamlit command
st.set_page_config(page_title="AI Support Analytics", layout="wide", page_icon="✨", initial_sidebar_state="expanded")

# --- Custom Premium CSS ---
st.markdown("""
<style>
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Backgrounds & Global Font */
    .stApp {
        background-color: #f8fafc;
        font-family: 'Inter', 'Segoe UI', sans-serif;
        color: #0f172a;
    }
    
    /* Force Wide Layout */
    .block-container {
        max-width: 95% !important;
        padding-top: 1rem !important;
        padding-right: 2rem !important;
        padding-left: 2rem !important;
        padding-bottom: 0.5rem !important;
    }
    
    /* Headers & Text overrides */
    h1, h2, h3, h4, h5, h6, p, span {
        color: #0f172a !important;
    }
    
    /* Premium Metric Cards */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-top: 4px solid #2563eb;
        padding: 10px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px rgba(37, 99, 235, 0.1);
    }
    div[data-testid="metric-container"] label {
        color: #475569 !important;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #1e293b !important;
    }
    
    /* Chat Input Enlargement */
    div[data-testid="stChatInput"] {
        padding-bottom: 25px;
    }
    div[data-testid="stChatInput"] textarea {
        font-size: 1.1em !important;
        padding: 15px 20px !important;
        border-radius: 12px !important;
        border: 1px solid #93c5fd !important;
        background-color: #ffffff !important;
        color: #0f172a !important;
    }
    
    /* Sidebar Premium Styling */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label span:first-child { display: none; }
    
    section[data-testid="stSidebar"] div[role="radiogroup"] label {
        padding: 12px 20px;
        margin-bottom: 8px;
        background-color: #ffffff;
        border-radius: 8px;
        transition: all 0.3s ease;
        cursor: pointer;
        color: #475569 !important;
        border: 1px solid transparent;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background-color: #eff6ff;
        color: #1d4ed8 !important;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label[aria-checked="true"] {
        background-color: #2563eb;
        color: white !important;
        box-shadow: 0 4px 10px rgba(37, 99, 235, 0.3);
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label[aria-checked="true"] p {
        color: white !important;
        font-weight: bold;
    }
    
    /* Dataframes */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #e2e8f0;
        background-color: #ffffff;
    }
    /* Code block styling (Make it white/light gray with dark text) */
    div[data-testid="stCodeBlock"] {
        background-color: #f8fafc !important;
    }
    div[data-testid="stCodeBlock"] pre {
        background-color: #f8fafc !important;
    }
    div[data-testid="stCodeBlock"] code {
        color: #0f172a !important;
        background-color: #f8fafc !important;
    }
    
    /* Bottom chat input area container (Force it to match the light theme) */
    div[data-testid="stBottomBlockContainer"], 
    div[data-testid="stChatInputContainer"],
    section[data-testid="stBottom"],
    .stChatInput {
        background-color: transparent !important;
    }
    
    /* Target the black block specifically */
    div[class*="stChatInput"] > div {
        background-color: transparent !important;
    }
    
    /* Fix invisible blinking text cursor in the search bar */
    .stChatInput textarea {
        caret-color: #0f172a !important;
        color: #0f172a !important;
    }
    
    /* Make the Send Button Icon Dark and Larger */
    button[data-testid="stChatInputSubmitButton"] svg {
        fill: #0f172a !important;
        color: #0f172a !important;
        width: 24px !important;
        height: 24px !important;
        transform: scale(1.2);
    }
    button[data-testid="stChatInputSubmitButton"] {
        color: #0f172a !important;
        padding-right: 15px !important;
    }
    
</style>
""", unsafe_allow_html=True)

# --- Sidebar Navigation ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/8633/8633190.png", width=60)
    st.markdown("<h2 style='color: #1e293b; font-weight: 800; margin-top:-15px;'>SupportOS</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; margin-top:-15px; margin-bottom: 25px;'>Enterprise AI Analytics</p>", unsafe_allow_html=True)
    
    page = st.radio("Navigation", ["📊 Dashboard View", "✨ AI Chat Assistant", "🚨 Anomaly Radar", "🔍 Raw Datagrid"], label_visibility="collapsed")
    st.divider()
    
    # Status indicators
    st.markdown("""
        <div style="background: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                <div style="width: 12px; height: 12px; border-radius: 50%; background-color: #10b981; box-shadow: 0 0 8px rgba(16, 185, 129, 0.5);"></div>
                <span style="font-size: 0.9em; color: #334155; font-weight: 600;">DuckDB Engine</span>
            </div>
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 12px; height: 12px; border-radius: 50%; background-color: #10b981; box-shadow: 0 0 8px rgba(16, 185, 129, 0.5);"></div>
                <span style="font-size: 0.9em; color: #334155; font-weight: 600;">Groq Llama 3.1</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

# Helper to format dataframes consistently
def format_dataframe(df):
    if df is not None and not df.empty:
        if 'created_at' in df.columns:
            # Replace 'T' and format to YYYY-MM-DD HH:MM
            try:
                df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
            except:
                pass
    return df

# Helper to load data
@st.cache_data(ttl=60)
def load_data():
    csv_path = "support_tickets.csv"
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        return format_dataframe(df)
    return None

df = load_data()

# --- Page: Dashboard ---
if page == "📊 Dashboard View":
    st.markdown("<h1 style='color: #0f172a;'>Welcome back, Admin 👋</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #475569; font-size: 1.1em;'>Here is the real-time overview of your support operations.</p>", unsafe_allow_html=True)
    st.write("")
    
    if df is not None:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Tickets", len(df))
        col2.metric("Open Tickets", len(df[df['status'] == 'Open']))
        col3.metric("Resolved", len(df[df['status'] == 'Resolved']))
        col4.metric("Critical Priority", len(df[df['priority'] == 'Critical']))
        
        
        
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            st.markdown("### 🗂️ Tickets by Category")
            st.bar_chart(df['category'].value_counts(), color="#3b82f6", use_container_width=True, height=220)
            
        with col_chart2:
            st.markdown("### 🔥 Tickets by Priority")
            st.bar_chart(df['priority'].value_counts(), color="#ef4444", use_container_width=True, height=220)
            
    else:
        st.error("Dataset not found. Please upload 'support_tickets.csv'.")

# --- Page: Ask AI (Chat) ---
elif page == "✨ AI Chat Assistant":
    st.markdown("<h1 style='color: #0f172a;'>✨ Ask your Data Anything</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #475569;'>Type a natural language question below. Groq will instantly convert it to secure SQL.</p>", unsafe_allow_html=True)
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if "sql" in message:
                st.markdown(f"<span style='font-size: 1.1em; color: #0f172a;'>{message['content']}</span>", unsafe_allow_html=True)
                if message.get("data"):
                    # Convert to dataframe only on render
                    chat_df = pd.DataFrame(message["data"])
                    st.dataframe(format_dataframe(chat_df), use_container_width=True, hide_index=True)
            else:
                st.markdown(f"<span style='color: #0f172a;'>{message['content']}</span>", unsafe_allow_html=True)

    if prompt := st.chat_input("➤ E.g., What is the average resolution time for Technical tickets?"):
        st.chat_message("user").markdown(f"<span style='color: #0f172a;'>{prompt}</span>", unsafe_allow_html=True)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner("Processing through Groq LPU Network..."):
                try:
                    res = requests.post(f"{API_URL}/query", json={"question": prompt}, timeout=130)
                    if res.status_code == 200:
                        data = res.json()
                        if data.get("success"):
                            st.markdown(f"<span style='font-size: 1.1em; color: #16a34a;'><b>{data['answer']}</b></span>", unsafe_allow_html=True)
                            
                            if data.get("data"):
                                chat_df_new = pd.DataFrame(data["data"])
                                st.dataframe(format_dataframe(chat_df_new), use_container_width=True, hide_index=True)
                                
                            st.session_state.messages.append({
                                "role": "assistant", 
                                "content": data["answer"],
                                "sql": data.get("sql"),
                                "data": data.get("data") # Store raw list of dicts, NOT a dataframe!
                            })
                        else:
                            st.error(f"Execution failed: {data.get('error')}")
                except Exception as e:
                    st.error(f"API Unreachable. Is the backend running? {e}")

# --- Page: Anomalies ---
elif page == "🚨 Anomaly Radar":
    st.markdown("<h1 style='color: #0f172a;'>🚨 Automated Threat & Anomaly Radar</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #475569;'>Identifies statistical outliers (Isolation Forest) and breached business rules instantly.</p>", unsafe_allow_html=True)
    
    if st.button("🚀 Execute Database Scan", type="primary", use_container_width=True):
        with st.spinner("Running AI anomaly detection..."):
            try:
                res = requests.get(f"{API_URL}/anomalies")
                if res.status_code == 200:
                    data = res.json()
                    st.success(f"Scan complete. {data.get('count', 0)} anomalies detected.")
                    if data.get('count', 0) > 0:
                        anomalies_df = format_dataframe(pd.DataFrame(data['anomalies']))
                        st.dataframe(
                            anomalies_df.style.map(lambda x: 'background-color: rgba(239, 68, 68, 0.1)' if x == 'Critical' else ''),
                            use_container_width=True, hide_index=True
                        )
                else:
                    st.error(f"Error: {res.text}")
            except Exception as e:
                st.error(f"Connection error: {e}")

# --- Page: Data Explorer ---
elif page == "🔍 Raw Datagrid":
    st.markdown("<h1 style='color: #0f172a;'>🔍 Enterprise Datagrid</h1>", unsafe_allow_html=True)
    if df is not None:
        col1, col2, col3 = st.columns(3)
        category = col1.selectbox("Department", ["All"] + list(df['category'].dropna().unique()))
        priority = col2.selectbox("Severity Level", ["All"] + list(df['priority'].dropna().unique()))
        status = col3.selectbox("State", ["All"] + list(df['status'].dropna().unique()))
        
        filtered_df = df.copy()
        if category != "All": filtered_df = filtered_df[filtered_df['category'] == category]
        if priority != "All": filtered_df = filtered_df[filtered_df['priority'] == priority]
        if status != "All": filtered_df = filtered_df[filtered_df['status'] == status]
        
        st.caption(f"Currently viewing {len(filtered_df)} records")
        st.dataframe(filtered_df, use_container_width=True, hide_index=True, height=600)
    else:
        st.info("No data available.")
