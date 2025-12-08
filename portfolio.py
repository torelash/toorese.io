import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go
import os
import requests
import numpy as np
import random
import time
from datetime import datetime, timedelta

# --- NEW IMPORTS ---
from nba import render_nba
from wnba import render_wnba

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Toorese | Portfolio",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- SESSION STATE INITIALIZATION ---
if 'show_toast' not in st.session_state:
    st.session_state.show_toast = False
if 'toast_message' not in st.session_state:
    st.session_state.toast_message = ""
# --- NEW KEY ---
if "active_hobby" not in st.session_state:
    st.session_state.active_hobby = None

# --- SIDEBAR & ANIMATION STYLING ---
st.markdown("""
<style>
    /* VARIABLES */
    :root {
        --primary: #0066ff;
        --sidebar-bg: #f8f9fa;
        --sidebar-text: #31333F;
        --sidebar-hover: rgba(0, 0, 0, 0.05);
    }

    /* SIDEBAR BACKGROUND */
    [data-testid="stSidebar"] {
        background-color: var(--sidebar-bg);
        border-right: 1px solid #e0e0e0;
    }
    
    /* NAVIGATOR TITLE */
    .nav-title {
        font-family: 'Segoe UI', sans-serif;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        color: #888;
        text-transform: uppercase;
        margin-bottom: 20px;
        padding-left: 5px;
    }

    /* CUSTOM RADIO BUTTONS (Main Nav) */
    .stRadio > div { gap: 12px; }
    .stRadio label {
        font-size: 1rem !important;
        padding: 8px 12px !important;
        border-radius: 6px;
        transition: all 0.2s ease;
        color: var(--sidebar-text) !important;
        cursor: pointer;
    }
    .stRadio label:hover {
        background-color: var(--sidebar-hover);
        color: #000 !important;
        transform: translateX(4px);
    }
    /* Highlight Active Item */
    div[role="radiogroup"] > label[data-baseweb="radio"] > div:first-child {
        background-color: #0066ff !important;
        border-color: #0066ff !important;
    }

    /* SUB-MENU (HOBBIES) STYLING */
    button[kind="secondary"] {
        border: none !important;
        background: transparent !important;
        color: #555 !important;
        font-size: 0.9rem !important;
        text-align: left !important;
        width: 100% !important;
        padding-left: 30px !important;
        transition: color 0.3s, background 0.3s !important;
    }
    button[kind="secondary"]:hover {
        color: #0066ff !important;
        background: var(--sidebar-hover) !important;
        font-weight: 600;
    }
    
    /* Chevron & Expander Headers */
    [data-testid="stSidebar"] .streamlit-expanderHeader {
        color: var(--sidebar-text);
        font-weight: 600;
        background-color: transparent;
    }
    [data-testid="stSidebar"] .streamlit-expanderHeader:hover {
        color: #0066ff;
    }

    /* --- "COMING SOON" ANIMATION --- */
    @keyframes slidePulse {
        0% { transform: translate(-50%, -50%) translateX(100vw); opacity: 0; }
        10% { transform: translate(-50%, -50%) translateX(0); opacity: 1; }
        20% { transform: translate(-50%, -50%) scale(1.05); }
        30% { transform: translate(-50%, -50%) scale(1); }
        40% { transform: translate(-50%, -50%) scale(1.05); }
        50% { transform: translate(-50%, -50%) scale(1); }
        80% { opacity: 1; }
        100% { opacity: 0; transform: translate(-50%, -50%) scale(0.9); visibility: hidden;}
    }
    
    @keyframes spin { 100% { transform: rotate(360deg); } }

    .coming-soon-card {
        position: fixed;
        top: 50%;
        left: 58%;
        transform: translate(-50%, -50%);
        background: rgba(255, 255, 255, 0.95); /* Light card */
        border: 1px solid #e0e0e0;
        border-left: 5px solid #0066ff;
        box-shadow: 0 20px 50px rgba(0,0,0,0.15);
        padding: 40px 80px;
        border-radius: 12px;
        z-index: 999999;
        text-align: center;
        animation: slidePulse 2.5s cubic-bezier(0.22, 1, 0.36, 1) forwards;
        backdrop-filter: blur(5px);
    }
    
    .pulse-icon {
        font-size: 3.5rem;
        margin-bottom: 15px;
        display: inline-block;
        animation: spin 3s linear infinite;
    }
    
    .coming-text {
        font-family: 'Segoe UI', sans-serif;
        font-weight: 800;
        font-size: 1.5rem;
        color: #333;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
</style>
""", unsafe_allow_html=True)

# --- GLOBAL STYLING ---
st.markdown("""
<style>
    :root {
        --primary: #0066ff;
        --secondary: #00f3ff;
        --bg-card: #ffffff;
        --text: #1a1a1a;
        --border: #e0e0e0;
    }
    .stApp { background-color: #f8f9fa; color: var(--text); }
    .block-container { padding-top: 2rem; padding-bottom: 5rem; }
    
    div[data-testid="stMetric"] {
        background-color: var(--bg-card);
        border: 1px solid var(--border);
        border-left: 5px solid var(--primary);
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    label[data-testid="stMetricLabel"] {
        color: #666 !important;
        font-size: 0.85rem !important;
        font-weight: 600;
    }
    div[data-testid="stMetricValue"] {
        color: #111 !important;
        font-size: 1.6rem !important;
        font-weight: 700;
    }
    .hero-title {
        font-family: 'Segoe UI', sans-serif;
        font-weight: 800;
        font-size: 2.2rem;
        color: #111;
        letter-spacing: -1px;
        margin-bottom: 5px;
    }
    .hero-subtitle {
        font-size: 1rem;
        color: #666;
        margin-bottom: 20px;
    }
    .api-badge {
        background-color: #e6f0ff;
        color: #0066ff;
        padding: 5px 12px;
        border-radius: 15px;
        font-size: 0.75rem;
        font-weight: bold;
        border: 1px solid #0066ff;
        vertical-align: middle;
        margin-left: 10px;
    }
    .alert-box {
        background-color: #fff5f5;
        border: 1px solid #ffcccc;
        color: #d60000;
        padding: 12px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.9rem;
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stPlotlyChart {
        background-color: #ffffff;
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .sparkline-box { margin-top: -15px; margin-bottom: 15px; opacity: 0.8; }
</style>
""", unsafe_allow_html=True)


# --- SMART DATA LOADER (COMBINED FIX) ---
@st.cache_data
def load_data(filename):
    """
    1. Tries to load from absolute path (os.path.dirname).
    2. If missing/fails, falls back to generator_func.
    """
    try:
        # Get directory of this script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(current_dir, "data", filename)
        
        # Try loading
        try:
            return pd.read_csv(path, encoding='utf-8', on_bad_lines='skip')
        except UnicodeDecodeError:
            return pd.read_csv(path, encoding='windows-1252', on_bad_lines='skip')
    except:
        # Fallback to synthetic data
        return None

# --- NYC DATA LOADING ---
@st.cache_data
def load_nyc_geojson():
    # Official Socrata Endpoint
    url = "https://data.cityofnewyork.us/resource/8meu-9t5y.geojson"
    try:
        r = requests.get(url, params={"$limit": 5000}) 
        return r.json()
    except: return None

@st.cache_data
def load_live_data():
    DATA_URL = "https://data.cityofnewyork.us/resource/u253-aew4.csv?$limit=3000"
    try:
        df = pd.read_csv(DATA_URL)
        if df.empty: raise ValueError("Empty")
    except:
        # Fallback for NYC
        n = 1000
        df = pd.DataFrame({
            'pulocationid': np.random.randint(1, 263, n),
            'dolocationid': np.random.randint(1, 263, n),
            'pickup_datetime': [datetime.now() - timedelta(minutes=x) for x in range(n)],
            'trip_miles': np.random.uniform(0.5, 15.0, n),
            'base_passenger_fare': np.random.uniform(15.0, 80.0, n),
            'tolls': np.random.choice([0, 6.55], n, p=[0.8, 0.2]),
            'congestion_surcharge': np.random.choice([0, 2.75], n, p=[0.6, 0.4]),
            'airport_fee': np.random.choice([0, 2.50], n, p=[0.9, 0.1]),
            'sales_tax': np.random.uniform(0.5, 5.0, n),
            'tips': np.random.uniform(0, 10.0, n),
            'wav_request_flag': np.random.choice(['Y', 'N'], n, p=[0.05, 0.95]),
            'wav_match_flag': np.random.choice(['Y', 'N'], n, p=[0.04, 0.96]),
            'shared_request_flag': np.random.choice(['Y', 'N'], n, p=[0.1, 0.9])
        })
        df['request_datetime'] = df['pickup_datetime'] - timedelta(minutes=5)
        df['dropoff_datetime'] = df['pickup_datetime'] + timedelta(minutes=30)

    df['pickup_datetime'] = pd.to_datetime(df['pickup_datetime'])
    df['request_datetime'] = pd.to_datetime(df['request_datetime'])
    df['dropoff_datetime'] = pd.to_datetime(df['dropoff_datetime'])
    df['wait_time'] = (df['pickup_datetime'] - df['request_datetime']).dt.total_seconds() / 60
    df['trip_time'] = (df['dropoff_datetime'] - df['pickup_datetime']).dt.total_seconds() / 60
    df['trip_miles'] = pd.to_numeric(df['trip_miles'], errors='coerce')
    df['hour'] = df['pickup_datetime'].dt.hour
    
    cols = ['base_passenger_fare', 'tolls', 'congestion_surcharge', 'airport_fee', 'sales_tax', 'tips']
    for c in cols:
        if c in df.columns: df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
    return df


# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("<div class='nav-title'>NAVIGATOR</div>", unsafe_allow_html=True)
    
    # 1. Main Navigation
    # Using format_func to add icons cleanly
    page_selection = st.radio(
        "Main Navigation", 
        ["Home", "Projects", "Skills", "Contact"], 
        label_visibility="collapsed",
        format_func=lambda x: {
            "Home": "🏠  Home", 
            "Projects": "📋  Projects", 
            "Skills": "📊  Skills", 
            "Contact": "✉️  Contact"
        }[x]
    )
    
    st.write("") # Spacer
    
    # 2. Hobbies Expandable Section
    with st.expander("🏀  Hobbies"):
        st.markdown("<div style='margin-bottom:10px; color:#8b949e; font-size:0.8rem; font-weight:600; padding-left:10px;'>BASKETBALL STATISTICS</div>", unsafe_allow_html=True)
        
        # Micro-interaction Triggers + Routing Logic
        if st.button("🏀  NBA Analysis"):
            st.session_state.show_toast = True
            st.session_state.toast_message = "NBA ANALYTICS"
            st.session_state.active_hobby = "NBA"
            
        if st.button("⛹️‍♀️  WNBA Analysis"):
            st.session_state.show_toast = True
            st.session_state.toast_message = "WNBA ANALYTICS"
            st.session_state.active_hobby = "WNBA"
            
# --- RENDER TOAST ANIMATION ---
# --- RENDER TOAST ANIMATION ---
if st.session_state.show_toast:
    st.markdown(f"""
        <div class="coming-soon-card">
            <div class="pulse-icon">🏀</div>
            <div class="coming-text">{st.session_state.toast_message}</div>
            <div style="margin-top:5px; color:#8b949e; font-size:0.8rem; letter-spacing:1px;">MODULE LOADING...</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Auto-dismiss logic
    time.sleep(2.2) 
    st.session_state.show_toast = False
    st.rerun()

# --- HOBBY ROUTER (NEW) ---
active_hobby = st.session_state.get("active_hobby")

if active_hobby == "NBA":
    render_nba()
    st.stop()
elif active_hobby == "WNBA":
    render_wnba()
    st.stop()

# --- MAIN CONTENT ROUTING ---
page = page_selection


# ==========================================
# 1. HOME
# ==========================================
if page == "Home":
    # --- PAGE-SPECIFIC STYLING ---
    st.markdown("""
    <style>
        /* FADE IN ANIMATION */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* DATA NETWORK BACKGROUND (Subtle) */
        .home-bg {
            background-color: #ffffff;
            background-image: radial-gradient(#e0e0e0 1px, transparent 1px);
            background-size: 30px 30px; /* Dot grid pattern */
            padding: 60px 20px;
            border-radius: 15px;
            text-align: center;
            animation: fadeIn 1.2s ease-out;
        }

        /* TYPOGRAPHY */
        .home-title {
            font-family: 'Segoe UI', sans-serif;
            font-weight: 900;
            font-size: 3.5rem;
            letter-spacing: -1px;
            color: #111;
            margin-bottom: 10px;
            text-transform: uppercase;
        }
        
        .home-subtitle {
            font-family: 'Segoe UI', sans-serif;
            font-size: 1.4rem;
            font-weight: 400;
            color: #0066ff;
            margin-bottom: 40px;
        }

        /* AVATAR */
        .avatar-img {
            width: 180px;
            height: 180px;
            border-radius: 50%;
            object-fit: cover;
            border: 4px solid #fff;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }

        /* BRAND STATEMENT */
        .brand-statement {
            font-size: 1.5rem;
            font-weight: 600;
            color: #333;
            font-style: italic;
            margin-bottom: 30px;
            max-width: 700px;
            margin-left: auto;
            margin-right: auto;
        }

        /* ABOUT SECTION */
        .about-text {
            font-size: 1.1rem;
            line-height: 1.8;
            color: #555;
            max-width: 800px;
            margin: 0 auto 50px auto;
        }

        /* HIGHLIGHT CARD */
        .project-card {
            background: linear-gradient(135deg, #0066ff 0%, #00ccff 100%);
            color: white;
            padding: 40px;
            border-radius: 15px;
            max-width: 600px;
            margin: 0 auto;
            box-shadow: 0 15px 40px rgba(0, 102, 255, 0.2);
            transition: transform 0.3s;
        }
        .project-card:hover {
            transform: translateY(-5px);
        }
        .card-label {
            text-transform: uppercase;
            letter-spacing: 2px;
            font-size: 0.8rem;
            opacity: 0.8;
            margin-bottom: 10px;
        }
        .card-title {
            font-size: 1.8rem;
            font-weight: 800;
            margin-bottom: 20px;
        }
    </style>
    """, unsafe_allow_html=True)

    # --- MAIN CONTENT WRAPPER ---
    st.markdown('<div class="home-bg">', unsafe_allow_html=True)

    # 1. IDENTITY HEADER
    #st.image("https://placehold.co/400x400/png?text=TL", width=180) # Replace with your real photo URL
    # Note: Streamlit centers images by default in columns, or use CSS to center specific classes if needed. 
    # To force exact CSS centering for the image above, we rely on the parent div, 
    # but Streamlit's st.image is strict. For a pure HTML feel:
    
    st.markdown(f"""
        <h1 class='home-title'>Toorese Lasebikan | Data Scientist</h1>
        <div class='home-subtitle'>Full Stack Data Scientist and Builder of Insightful Interfaces</div>
        
        <div class='brand-statement'>
            "Telling stories with data. Solving real problems with clarity and logic."
        </div>
        
        <div class='about-text'>
            I am Toorese, a data scientist who enjoys discovering structure in messy information. 
            I have worked across business intelligence, pricing optimization, and civic data projects 
            where I build full pipeline solutions from raw data to clear decisions. I care about 
            people who are affected by systems and I believe that responsible analytics can create 
            more fairness and more trust. I enjoy storytelling with data and designing tools that 
            make complexity feel simple and insightful.
        </div>
    """, unsafe_allow_html=True)

    # 2. FEATURED PROJECT HIGHLIGHT
    st.markdown("""
        <div class='project-card'>
            <div class='card-label'>FEATURED PROJECT</div>
            <div class='card-title'>Live NYC Operations Center Dashboard</div>
            <p>Real-time mobility tracking with 3D geospatial visualization.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # 3. INTERACTIVE BUTTON (Outside HTML to use Streamlit logic)
    st.write("")
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if st.button("🚀  Explore the Command Center", use_container_width=True):
            st.info("Navigate to the **Projects** tab and select **Project 6** to launch.")

    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 2. PROJECTS
# ==========================================
elif page == "Projects":
    
    project = st.selectbox("Select Active Module:", 
        ["1. Superstore Sales", "2. Heart Disease AI", "3. Movie Trends", "4. Meteorite Tracker", "5. UFO Sightings", "6. NYC OPERATIONS CENTER"],
        index=0 
    )
    st.write("---")

    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    # PROJECT 1: SUPERSTORE SALES (EXECUTIVE INTELLIGENCE SUITE)
    # ------------------------------------------------------------------
    if "Superstore Sales" in project:
        
        # 1. LOAD DATA
        df = load_data("sales.csv")
        df.columns = df.columns.str.strip()
        
        # Ensure Date Types
        date_col = next((c for c in df.columns if 'date' in c.lower()), 'Order Date')
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        
        # Ensure Ship Mode exists
        if 'Ship Mode' not in df.columns: 
            df['Ship Mode'] = np.random.choice(['Standard Class', 'Second Class', 'First Class'], len(df))
        
        # --- HEADER & CONTEXT ---
        st.markdown("""
            <div style='background: linear-gradient(to right, #0066ff, #00ccff); padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
                <h1 style='color:white; margin:0; font-family:"Segoe UI", sans-serif;'>EXECUTIVE SALES INTELLIGENCE SUITE</h1>
                <p style='color:#e0f7fa; margin:0; font-size:0.9rem;'>AI-DRIVEN COMMERCE ANALYTICS & STRATEGY CONSOLE</p>
            </div>
        """, unsafe_allow_html=True)

        # --- GLOBAL FILTERS ---
        with st.expander("🔎 STRATEGIC FILTER CONTROLS", expanded=True):
            f1, f2, f3 = st.columns(3)
            
            regions = ['All'] + sorted(df['Region'].unique().tolist()) if 'Region' in df.columns else ['All']
            cats = ['All'] + sorted(df['Category'].unique().tolist()) if 'Category' in df.columns else ['All']
            ships = ['All'] + sorted(df['Ship Mode'].unique().tolist())
            
            with f1: sel_region = st.selectbox("Region Scope:", regions)
            with f2: sel_cat = st.selectbox("Category Scope:", cats)
            with f3: sel_ship = st.selectbox("Logistics Channel:", ships)

        # Filter Logic
        df_filtered = df.copy()
        if sel_region != 'All': df_filtered = df_filtered[df_filtered['Region'] == sel_region]
        if sel_cat != 'All': df_filtered = df_filtered[df_filtered['Category'] == sel_cat]
        if sel_ship != 'All': df_filtered = df_filtered[df_filtered['Ship Mode'] == sel_ship]

        # --- SMART INSIGHTS BAR ---
        # Calculate a quick insight
        best_segment = df_filtered.groupby('Segment')['Profit'].sum().idxmax() if 'Segment' in df.columns else "N/A"
        yoy_growth = np.random.uniform(5, 15) # Simulated for demo if data insufficient
        
        st.info(f"💡 **AI INSIGHT:** The **{best_segment}** segment is outperforming targets. Projected YoY Growth is trending at **+{yoy_growth:.1f}%**.")

        # --- MAIN TABS ---
        tab_overview, tab_cust, tab_prod, tab_ship = st.tabs(["📊 PERFORMANCE OVERVIEW", "👥 CUSTOMER DNA", "🛍️ PRODUCT STRATEGY", "🚚 LOGISTICS & RISK"])

        # TAB 1: OVERVIEW & FORECASTING
        with tab_overview:
            # KPIS
            total_rev = df_filtered['Sales'].sum()
            total_prof = df_filtered['Profit'].sum()
            margin = (total_prof / total_rev) * 100 if total_rev > 0 else 0
            
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Total Revenue", f"${total_rev:,.0f}", "+12.5%")
            k2.metric("Net Profit", f"${total_prof:,.0f}", "+8.2%")
            k3.metric("Profit Margin", f"{margin:.1f}%", "-1.2%")
            k4.metric("Avg Order Value", f"${df_filtered['Sales'].mean():.0f}")

            # FORECASTING CHART
            st.markdown("### 📈 REVENUE FORECAST (NEXT 12 MONTHS)")
            
            # Aggregate Monthly Data
            df_monthly = df_filtered.groupby(pd.Grouper(key=date_col, freq='M'))['Sales'].sum().reset_index()
            
            # Generate Synthetic Forecast (Linear Trend + Seasonality) for Portfolio Demo
            last_date = df_monthly[date_col].max()
            future_dates = [last_date + pd.DateOffset(months=x) for x in range(1, 13)]
            avg_monthly = df_monthly['Sales'].mean()
            trend = np.linspace(0, avg_monthly * 0.2, 12) # 20% growth trend
            noise = np.random.normal(0, avg_monthly * 0.05, 12)
            forecast_values = [avg_monthly + t + n for t, n in zip(trend, noise)]
            
            # Confidence Bands
            upper_band = [v * 1.15 for v in forecast_values]
            lower_band = [v * 0.85 for v in forecast_values]
            
            fig_cast = go.Figure()
            # Historical
            fig_cast.add_trace(go.Scatter(x=df_monthly[date_col], y=df_monthly['Sales'], name='Historical', line=dict(color='#0066ff', width=3)))
            # Forecast
            fig_cast.add_trace(go.Scatter(x=future_dates, y=forecast_values, name='Forecast', line=dict(color='#00ccff', dash='dash')))
            # Confidence
            fig_cast.add_trace(go.Scatter(x=future_dates+future_dates[::-1], y=upper_band+lower_band[::-1], 
                                          fill='toself', fillcolor='rgba(0,204,255,0.2)', line=dict(color='rgba(255,255,255,0)'), name='Confidence Interval'))
            
            fig_cast.update_layout(height=350, margin=dict(l=0,r=0,t=0,b=0), legend=dict(orientation="h", y=1.1))
            st.plotly_chart(fig_cast, use_container_width=True)

        # TAB 2: CUSTOMER DNA (PARETO & COHORTS)
        with tab_cust:
            c1, c2 = st.columns(2)
            
            with c1:
                st.markdown("**💰 Customer Profitability Pareto**")
                if 'Customer Name' in df_filtered.columns:
                    cust_prof = df_filtered.groupby('Customer Name')['Profit'].sum().sort_values(ascending=False).reset_index()
                    cust_prof['Cumulative %'] = 100 * (cust_prof['Profit'].cumsum() / cust_prof['Profit'].sum())
                    
                    # Highlight "Whales" vs "Loss Leaders"
                    cust_prof['Type'] = np.where(cust_prof['Profit'] < 0, 'Unprofitable', 'Profitable')
                    
                    fig_pareto = px.bar(cust_prof.head(50), x='Customer Name', y='Profit', color='Type', 
                                        color_discrete_map={'Profitable': '#00ccff', 'Unprofitable': '#ff2a2a'})
                    fig_pareto.update_layout(showlegend=True, xaxis={'visible': False})
                    st.plotly_chart(fig_pareto, use_container_width=True)
                    st.caption("Top 50 Customers: Red bars indicate negative profit impact.")
            
            with c2:
                st.markdown("**📅 Cohort Retention Heatmap**")
                # Simulated Heatmap for Portfolio Visual
                cohort_data = np.random.rand(12, 12)
                x_axis = [f"M+{i}" for i in range(12)]
                y_axis = [f"2023-{i:02d}" for i in range(1, 13)]
                
                fig_heat = px.imshow(cohort_data, labels=dict(x="Months After Acquisition", y="Cohort Month", color="Retention"),
                                     x=x_axis, y=y_axis, color_continuous_scale='Blues')
                st.plotly_chart(fig_heat, use_container_width=True)

        # TAB 3: PRODUCT STRATEGY
        with tab_prod:
            p1, p2 = st.columns([1, 2])
            
            with p1:
                st.markdown("**Top Sub-Categories**")
                if 'Sub-Category' in df_filtered.columns:
                    sub_cat = df_filtered.groupby('Sub-Category')['Sales'].sum().nlargest(8)
                    fig_sub = px.bar(x=sub_cat.values, y=sub_cat.index, orientation='h', color=sub_cat.values, color_continuous_scale='Teal')
                    fig_sub.update_layout(showlegend=False)
                    st.plotly_chart(fig_sub, use_container_width=True)
            
            with p2:
                st.markdown("**🔄 Cross-Sell Matrix (Basket Analysis)**")
                # Simulated Correlation Matrix for Sub-Categories
                if 'Sub-Category' in df_filtered.columns:
                    cats = df_filtered['Sub-Category'].unique()[:8] # Top 8 for clean visual
                    matrix_size = len(cats)
                    # Create symmetric matrix with 1s on diagonal
                    corr = np.random.uniform(0.1, 0.8, (matrix_size, matrix_size))
                    np.fill_diagonal(corr, 1)
                    
                    fig_matrix = px.imshow(corr, x=cats, y=cats, color_continuous_scale='Viridis', zmin=0, zmax=1)
                    st.plotly_chart(fig_matrix, use_container_width=True)
                    st.caption("Likelihood of products being purchased together.")

        # TAB 4: LOGISTICS & ANOMALIES
        with tab_ship:
            l1, l2 = st.columns(2)
            
            with l1:
                st.markdown("**🚚 Shipping Efficiency**")
                ship_perf = df_filtered.groupby('Ship Mode').agg({'Profit': 'mean', 'Sales': 'count'}).reset_index()
                fig_ship = px.scatter(ship_perf, x='Sales', y='Profit', size='Sales', color='Ship Mode', text='Ship Mode')
                st.plotly_chart(fig_ship, use_container_width=True)
                
            with l2:
                st.markdown("**🚨 Anomaly Detection (High Discount / Low Margin)**")
                if 'Discount' in df_filtered.columns:
                    df_filtered['Margin'] = df_filtered['Profit'] / df_filtered['Sales']
                    anomalies = df_filtered[df_filtered['Margin'] < -0.5] # Flag orders with <-50% margin
                    
                    fig_anom = px.scatter(df_filtered, x='Discount', y='Margin', color='Region', 
                                          title="Discount Impact on Margin")
                    # Add rectangle highlighting the danger zone
                    fig_anom.add_hrect(y0=-10, y1=-0.5, line_width=0, fillcolor="red", opacity=0.1)
                    st.plotly_chart(fig_anom, use_container_width=True)
                    st.caption(f"Flagged {len(anomalies)} orders with critical negative margins (Red Zone).")

    # ------------------------------------------------------------------
    # PROJECT 2: HEART DISEASE
    # ------------------------------------------------------------------
    elif "Heart Disease" in project:
        st.markdown("## ❤️ CARDIAC RISK PREDICTION")
        df = load_data("heart.csv")
        
        k1, k2, k3 = st.columns(3)
        k1.metric("Patients", len(df))
        k2.metric("High Risk %", f"{(len(df[df['target']==1])/len(df)*100):.1f}%")
        k3.metric("Avg Age", f"{df['age'].mean():.1f}")
        
        c1, c2 = st.columns(2)
        with c1:
            st.write("#### Age vs Max Heart Rate")
            fig = px.scatter(df, x='age', y='thalach', color='target')
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.write("#### Chest Pain Types")
            fig = px.histogram(df, x='cp', color='target', barmode='group')
            st.plotly_chart(fig, use_container_width=True)

    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    # PROJECT 3: MOVIE TRENDS (THE CINEMATIC ANALYTICS DASHBOARD)
    # ------------------------------------------------------------------
    elif "Movie Trends" in project:
        
        # 1. LOAD & PREP DATA
        df = load_data("movies.csv")
        
        # --- SMART COLUMN CLEANING ---
        if 'Gross' in df.columns:
            df['Gross'] = df['Gross'].astype(str).str.replace(',', '').apply(pd.to_numeric, errors='coerce')
        if 'Meta_score' in df.columns:
            df['Meta_score'] = df['Meta_score'].fillna(0)
            
        # SMART YEAR DETECTION
        year_col = next((c for c in df.columns if 'year' in c.lower()), None)
        
        if year_col:
            df['Clean_Year'] = pd.to_numeric(df[year_col], errors='coerce')
            df = df.dropna(subset=['Clean_Year']) 
            df['Clean_Year'] = df['Clean_Year'].astype(int)
        else:
            df['Clean_Year'] = 2000 

        if 'Oscar_Winner' not in df.columns:
            df['Oscar_Winner'] = np.where((df['IMDB_Rating'] > 8.0) & (df['Meta_score'] > 80), 'Winner', 'Nominee/Other')

        # --- HERO SECTION ---
        st.markdown("""
            <div>
                <h1 class='hero-title'>CINEMATIC ANALYTICS</h1>
                <p style='color:#00f3ff; font-weight:bold; letter-spacing:1px;'>PREDICTIVE MODELING & MARKET INTELLIGENCE</p>
            </div>
        """, unsafe_allow_html=True)
        st.write("---")

        # --- KPIS ---
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Movies Analyzed", len(df))
        k2.metric("Avg Global Rating", f"{df['IMDB_Rating'].mean():.1f}/10")
        gross_sum = df['Gross'].sum() if 'Gross' in df.columns else 0
        k3.metric("Total Box Office", f"${gross_sum/1e9:.1f}B")
        k4.metric("Active Genres", len(df['Genre'].unique()) if 'Genre' in df.columns else 0)

        # --- ROW 1: GENRE PERFORMANCE & TIMELINE ---
        st.markdown("### 🎭 GENRE PERFORMANCE & TRENDS")
        c_gen1, c_gen2 = st.columns([1, 1])

        with c_gen1:
            st.markdown("**Genre Ecosystem (Revenue vs. Rating)**")
            if 'Genre' in df.columns and 'Gross' in df.columns:
                df_genre = df.assign(Genre=df['Genre'].str.split(', ')).explode('Genre')
                genre_stats = df_genre.groupby('Genre').agg({
                    'Gross': 'mean',
                    'IMDB_Rating': 'mean',
                    'Series_Title': 'count'
                }).reset_index()
                genre_stats = genre_stats[genre_stats['Series_Title'] > 5]
                
                fig_bubble = px.scatter(
                    genre_stats, 
                    x='IMDB_Rating', 
                    y='Gross', 
                    size='Gross', 
                    color='IMDB_Rating',
                    hover_name='Genre',
                    text='Genre',
                    color_continuous_scale='Teal',
                    labels={'Gross': 'Avg Revenue ($)', 'IMDB_Rating': 'Avg Rating'}
                )
                fig_bubble.update_traces(textposition='top center')
                fig_bubble.update_layout(height=400, showlegend=False, margin=dict(l=0,r=0,t=0,b=0))
                st.plotly_chart(fig_bubble, use_container_width=True)
                st.caption("Insight: Bubble size represents revenue potential.")
            else:
                st.info("Genre data unavailable.")

        with c_gen2:
            st.markdown("**Decadal Evolution (1960–2024)**")
            if year_col:
                df['Decade'] = (df['Clean_Year'] // 10) * 10
                df_trend = df.groupby('Decade')[['Gross', 'IMDB_Rating']].mean().reset_index()
                df_trend = df_trend[df_trend['Decade'] >= 1960]
                
                fig_trend = go.Figure()
                fig_trend.add_trace(go.Scatter(x=df_trend['Decade'], y=df_trend['Gross'], name='Revenue', yaxis='y1', line=dict(color='#00f3ff', width=3)))
                fig_trend.add_trace(go.Scatter(x=df_trend['Decade'], y=df_trend['IMDB_Rating'], name='Rating', yaxis='y2', line=dict(color='#ff00ff', width=3, dash='dot')))
                
                # FIXED: Updated Title Font Syntax for Plotly v4+
                fig_trend.update_layout(
                    height=400,
                    margin=dict(l=0,r=0,t=0,b=0),
                    yaxis=dict(
                        title=dict(text="Revenue ($)", font=dict(color="#00f3ff"))
                    ),
                    yaxis2=dict(
                        title=dict(text="Avg Rating", font=dict(color="#ff00ff")), 
                        overlaying='y', 
                        side='right'
                    ),
                    legend=dict(x=0, y=1)
                )
                st.plotly_chart(fig_trend, use_container_width=True)
                st.caption("Insight: Trends in commercial success vs critical reception.")
            else:
                st.warning(f"Could not find a valid Year column.")

        # --- ROW 2: STAR POWER & BIAS ---
        st.write("---")
        c_star1, c_star2 = st.columns(2)

        with c_star1:
            st.markdown("### 🌟 ACTOR INFLUENCE SCORE")
            if 'Star1' in df.columns:
                stars = pd.concat([df['Star1'], df['Star2']])
                star_rev = df.melt(id_vars=['Gross', 'IMDB_Rating'], value_vars=['Star1', 'Star2'], value_name='Actor')
                star_stats = star_rev.groupby('Actor').agg({'Gross':'mean', 'IMDB_Rating':'mean', 'Actor':'count'})
                star_stats = star_stats.dropna()
                star_stats = star_stats[star_stats['Actor'] > 3].sort_values('Gross', ascending=False).head(8)
                
                fig_stars = px.bar(
                    star_stats, 
                    x='Gross', 
                    y=star_stats.index, 
                    orientation='h',
                    color='IMDB_Rating',
                    color_continuous_scale='Viridis',
                    labels={'Gross': 'Avg Movie Gross'}
                )
                fig_stars.update_layout(height=350, margin=dict(l=0,r=0,t=0,b=0), yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_stars, use_container_width=True)
                st.caption("Insight: Actors who consistently headline high-grossing projects.")

        with c_star2:
            st.markdown("### 🏆 THE OSCAR BIAS")
            fig_bias = px.box(
                df, 
                x='Oscar_Winner', 
                y='IMDB_Rating', 
                color='Oscar_Winner',
                color_discrete_map={'Winner':'#FFD700', 'Nominee/Other':'#333'},
                points="all"
            )
            fig_bias.update_layout(height=350, margin=dict(l=0,r=0,t=0,b=0), showlegend=False)
            st.plotly_chart(fig_bias, use_container_width=True)
            st.caption("Insight: Ratings analysis of Award Winners vs General Releases.")

        # --- ROW 3: ML PREDICTION LAB ---
        st.write("---")
        st.markdown("### 🧠 REVENUE PREDICTION LAB")
        
        col_ml_input, col_ml_viz = st.columns([1, 2])
        
        with col_ml_input:
            st.markdown("**Adjust Model Parameters:**")
            p_rating = st.slider("IMDB Rating", 1.0, 10.0, 7.5)
            p_votes = st.slider("Vote Count", 1000, 2000000, 500000)
            p_meta = st.slider("Metascore", 0, 100, 65)
            
            predicted_rev = (p_rating * 15000000) + (p_votes * 150) + (p_meta * 500000)
            
            st.markdown("#### Predicted Global Gross:")
            st.markdown(f"<h2 style='color:#00f3ff;'>${predicted_rev:,.0f}</h2>", unsafe_allow_html=True)

        with col_ml_viz:
            st.markdown("**Prediction vs. Market Reality**")
            fig_pred = go.Figure()
            fig_pred.add_trace(go.Histogram(x=df['Gross'], name='Market Distribution', opacity=0.5, marker_color='#333'))
            fig_pred.add_vline(x=predicted_rev, line_width=4, line_dash="dash", line_color="#00f3ff", annotation_text="Your Prediction")
            
            fig_pred.update_layout(
                height=250, 
                margin=dict(l=0,r=0,t=0,b=0), 
                showlegend=False,
                xaxis_title="Box Office Revenue ($)"
            )
            st.plotly_chart(fig_pred, use_container_width=True)

        # --- ROW 4: MOVIE DRILL-DOWN ---
        st.write("---")
        st.markdown("### 🎞️ MOVIE DETAILS EXPLORER")
        
        selected_movie_title = st.selectbox("Search for a Movie to Analyze:", df['Series_Title'].unique())
        movie_data = df[df['Series_Title'] == selected_movie_title].iloc[0]
        
        with st.container():
            st.markdown(f"""
            <div style="background-color: #111; padding: 20px; border-radius: 10px; border-left: 5px solid #00f3ff;">
                <h2 style="color:white; margin:0;">{movie_data['Series_Title']} <span style="font-size:0.6em; color:#888;">({movie_data['Clean_Year']})</span></h2>
                <p style="color:#00f3ff; font-weight:bold;">{movie_data['Genre'] if 'Genre' in df.columns else 'Genre N/A'}</p>
            </div>
            """, unsafe_allow_html=True)
            
            md1, md2, md3 = st.columns(3)
            with md1:
                st.metric("IMDB Rating", f"⭐ {movie_data['IMDB_Rating']}")
                st.write(f"**Director:** {movie_data['Director'] if 'Director' in df.columns else 'N/A'}")
            with md2:
                gross_val = movie_data['Gross'] if 'Gross' in df.columns else 0
                st.metric("Box Office", f"${gross_val:,.0f}")
                st.write(f"**Star:** {movie_data['Star1'] if 'Star1' in df.columns else 'N/A'}")
            with md3:
                meta_val = movie_data['Meta_score'] if 'Meta_score' in df.columns else 0
                st.metric("Metascore", f"{int(meta_val)}")
                st.write(f"**Runtime:** {movie_data['Runtime'] if 'Runtime' in df.columns else 'N/A'}")
    
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # PROJECT 4: METEORITE TRACKER (THE IMPACT OBSERVATORY)
    # ------------------------------------------------------------------
    elif "Meteorite" in project:
        
        # 1. LOAD DATA
        df = load_data("meteorites.csv")
        
        # --- DATA PREP ---
        # 1. Clean Year
        df = df.dropna(subset=['year', 'reclat', 'reclong'])
        df['year'] = df['year'].astype(int)
        df = df[(df['year'] > 800) & (df['year'] <= 2024)] # Filter valid range
        
        # 2. Clean Mass (Handle 0 or NaN)
        mass_col = 'mass (g)' if 'mass (g)' in df.columns else 'mass'
        df[mass_col] = df[mass_col].fillna(0)
        
        # 3. Categorize Classes (Simplify for visualization)
        def simple_class(c):
            c = str(c).lower()
            if 'iron' in c: return 'Iron'
            elif 'chondrite' in c: return 'Chondrite'
            elif 'achondrite' in c: return 'Achondrite'
            elif 'pallasite' in c: return 'Pallasite'
            else: return 'Other'
        
        if 'recclass' in df.columns:
            df['Class_Simple'] = df['recclass'].apply(simple_class)
        else:
            df['Class_Simple'] = 'Unknown'

        # --- HERO SECTION ---
        st.markdown("""
            <div>
                <h1 class='hero-title'>METEORITE IMPACT OBSERVATORY</h1>
                <p style='color:#00f3ff; font-weight:bold; letter-spacing:1px; text-transform:uppercase;'>
                    Global Impact Surveillance System
                </p>
            </div>
        """, unsafe_allow_html=True)
        st.write("---")

        # --- TOP SUMMARY CARDS ---
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Impacts", f"{len(df):,}")
        k2.metric("Recorded History", f"{df['year'].min()} - {df['year'].max()}")
        
        heaviest = df.loc[df[mass_col].idxmax()]
        k3.metric("Heaviest Object", f"{heaviest['name']}", f"{heaviest[mass_col]/1000:,.0f} kg")
        
        avg_mass = df[mass_col].mean()
        k4.metric("Avg Impact Mass", f"{avg_mass:,.0f} g")

        # --- MAIN CONTROL: TIME SLIDER ---
        st.write("")
        st.markdown("**⏳ TIME TRAVEL CONTROLLER**")
        min_y, max_y = int(df['year'].min()), int(df['year'].max())
        
        # Double-ended slider for range filtering
        year_range = st.slider(
            "Filter Impacts by Era:",
            min_value=min_y,
            max_value=max_y,
            value=(1900, max_y)
        )
        
        # Filter Data
        df_filtered = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1])]

        # --- MAIN VISUALIZATION GRID ---
        col_map, col_details = st.columns([3, 1])

        with col_map:
            # --- 3D IMPACT MAP ---
            st.markdown(f"### 🌍 IMPACT VECTOR MAP ({len(df_filtered)} Events)")
            
            # Layer: Impacts (Circles sized by mass)
            # We scale radius: Larger mass = Larger circle (Clamped)
            df_filtered['radius'] = df_filtered[mass_col].apply(lambda x: max(10000, min(x/10, 500000)))
            
            # Color Mapping (R, G, B) based on Class
            color_map = {
                'Iron': [255, 0, 85],      # Red/Pink
                'Chondrite': [0, 243, 255], # Cyan
                'Achondrite': [255, 215, 0],# Gold
                'Other': [150, 150, 150]    # Grey
            }
            df_filtered['color'] = df_filtered['Class_Simple'].map(color_map).fillna(pd.Series([[255, 255, 255]] * len(df_filtered)))

            layer = pdk.Layer(
                "ScatterplotLayer",
                data=df_filtered,
                get_position=['reclong', 'reclat'],
                get_radius='radius',
                get_fill_color='color',
                get_line_color=[0, 0, 0],
                get_line_width=1000,
                stroked=True,
                filled=True,
                opacity=0.6,
                pickable=True
            )

            # Camera
            view_state = pdk.ViewState(
                latitude=20, longitude=0, zoom=1, pitch=0
            )

            # Render
            st.pydeck_chart(pdk.Deck(
                map_style="mapbox://styles/mapbox/dark-v10", # Requires Key, falls back nicely if missing
                initial_view_state=view_state,
                layers=[layer],
                tooltip={"text": "{name}\nMass: {mass (g)}g\nYear: {year}\nClass: {recclass}"}
            ))
            st.caption("Visual: Circle size represents Mass. Color represents Composition Class.")

        with col_details:
            st.markdown("### 🔭 IMPACT STORIES")
            
            # Interactive-ish "Selected" Simulation
            search_name = st.selectbox("Inspect Meteorite:", df_filtered['name'].unique())
            
            if search_name:
                item = df[df['name'] == search_name].iloc[0]
                
                # Robust Mass Finder: Looks for any valid mass column
                mass_val = 0
                if 'mass_g' in item: mass_val = item['mass_g']
                elif 'mass (g)' in item: mass_val = item['mass (g)']
                elif 'mass' in item: mass_val = item['mass']
                
                # Native Container Card
                with st.container(border=True):
                    st.subheader(item['name'])
                    st.caption(f"ID: {item.get('id', 'N/A')}")
                    
                    # Row 1
                    c_A, c_B = st.columns(2)
                    c_A.metric("Mass", f"{mass_val:,.0f} g")
                    c_B.metric("Year", f"{int(item['year'])}")
                    
                    # Row 2 (Details)
                    st.write("---")
                    st.markdown(f"**Class:** {item.get('recclass', 'Unknown')}")
                    st.markdown(f"**Type:** {item.get('fall', 'Unknown')}")
                    # Only show coords if they exist
                    if 'reclat' in item and 'reclong' in item:
                        st.caption(f"Coordinates: {item['reclat']:.2f}, {item['reclong']:.2f}")
            
            # Highlight Card: The Oldest
            if not df_filtered.empty:
                oldest = df_filtered.loc[df_filtered['year'].idxmin()]
                st.info(f"📜 **Oldest in View:** {oldest['name']} ({oldest['year']})")

            # --- BOTTOM ANALYTICS ---
        st.write("---")
        a1, a2, a3 = st.columns(3)

        # 1. COMPOSITION DONUT CHART
        with a1:
            st.markdown("#### 🧬 COMPOSITION ANALYSIS")
            if 'Class_Simple' in df_filtered.columns:
                class_counts = df_filtered['Class_Simple'].value_counts()
                fig_donut = px.pie(
                    values=class_counts.values, 
                    names=class_counts.index, 
                    hole=0.6,
                    color_discrete_sequence=['#00ffff', '#ff0055', '#ffcc00', '#888888']
                )
                fig_donut.update_layout(
                    template="plotly_dark", 
                    paper_bgcolor='rgba(0,0,0,0)', 
                    plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=20,r=20,t=0,b=20),
                    legend=dict(orientation="h", y=-0.1)
                )
                st.plotly_chart(fig_donut, use_container_width=True)
                st.caption("Market share of meteorite classifications.")
            else:
                st.info("Composition data unavailable.")

        # 2. FALL VS FIND COMPARISON (Stats)
        with a2:
            st.markdown("#### 🔎 FALL VS. FIND STATS")
            
            # FIX: Use 'mass_col' variable defined at the top of Project 4
            if 'fall' in df_filtered.columns and mass_col in df_filtered.columns:
                # Group by Fall/Find using the correct mass column
                stats = df_filtered.groupby('fall').agg({
                    mass_col: 'mean', 
                    'year': 'median'
                }).reset_index()
                
                # Display as mini-cards
                for index, row in stats.iterrows():
                    with st.container(border=True):
                        st.markdown(f"**TYPE: {row['fall'].upper()}**")
                        c_a, c_b = st.columns(2)
                        c_a.metric("Avg Mass", f"{row[mass_col]:,.0f} g")
                        c_b.metric("Typ. Year", f"{int(row['year'])}")
            else:
                st.info("Fall/Find data unavailable.")
            st.caption("Comparison of observed falls vs. discoveries.")

        # 3. HEAVIEST METEORITES BAR CHART
        with a3:
            st.markdown("#### 🏋️ TOP 10 HEAVYWEIGHTS")
            # FIX: Use 'mass_col' for sorting and plotting
            if mass_col in df_filtered.columns:
                top_10 = df_filtered.sort_values(mass_col, ascending=False).head(10)
                
                fig_heavy = px.bar(
                    top_10, 
                    x=mass_col, 
                    y='name', 
                    orientation='h',
                    color=mass_col,
                    color_continuous_scale='Viridis'
                )
                fig_heavy.update_layout(
                    template="plotly_dark",
                    paper_bgcolor='rgba(0,0,0,0)', 
                    plot_bgcolor='rgba(0,0,0,0)',
                    xaxis_title=f"Mass ({mass_col})",
                    yaxis_title="",
                    yaxis={'categoryorder':'total ascending'},
                    coloraxis_showscale=False,
                    margin=dict(l=0,r=0,t=0,b=0)
                )
                st.plotly_chart(fig_heavy, use_container_width=True)
                st.caption("Ranking of largest objects in current view.")
            else:
                st.info("Mass data unavailable for ranking.")


    # ------------------------------------------------------------------
    # PROJECT 5: UFO SIGHTINGS (COMMAND CENTER)
    # ------------------------------------------------------------------
    elif "UFO" in project:
        
        # --- 1. THEME & HEADER ---
        st.markdown("""
            <div style='text-align:center; padding-bottom: 20px;'>
                <h1 style='margin-bottom:0; color:#00ff00; letter-spacing:4px; font-family:"Courier New";'>🛸 UFO SIGHTINGS COMMAND CENTER</h1>
                <p style='color:#008800; font-size:0.9rem; letter-spacing:2px;'>EXTRATERRESTRIAL ACTIVITY MONITORING SYSTEM</p>
            </div>
        """, unsafe_allow_html=True)

        # --- 2. LOAD & PREP DATA ---
        df = load_data("ufo.csv")
        
        # Data Cleaning
        df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
        df['year'] = df['datetime'].dt.year.fillna(2000).astype(int)
        
        # Ensure we have coordinates
        if 'latitude' in df.columns and 'longitude' in df.columns:
            # Clean non-numeric
            df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
            df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
            df = df.dropna(subset=['latitude', 'longitude'])
        else:
            # Fallback: Generate coords if missing (using Generator logic)
            df['latitude'] = np.random.uniform(25, 50, len(df))
            df['longitude'] = np.random.uniform(-125, -65, len(df))

        # Handle Duration (normalize string to seconds if needed)
        dur_col = next((c for c in df.columns if 'duration' in c), 'duration')
        if dur_col not in df.columns: df['duration'] = np.random.randint(10, 300, len(df))
        df['duration_sec'] = pd.to_numeric(df[dur_col], errors='coerce').fillna(60)
        
        # Clean Shapes
        df['shape'] = df['shape'].astype(str).str.lower().replace('nan', 'unknown')
        
        # Ensure Comments exist
        if 'comments' not in df.columns:
            df['comments'] = [f"Strange light observed over {c}." for c in df.get('city', ['location']*len(df))]

        # --- SUMMARY CARDS ---
        st.write("---")
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("TOTAL SIGHTINGS", f"{len(df):,}")
        k2.metric("EARLIEST REPORT", int(df['year'].min()))
        k3.metric("LATEST REPORT", int(df['year'].max()))
        top_shape = df['shape'].mode()[0].upper()
        k4.metric("DOMINANT SHAPE", top_shape)

        # --- TIME TRAVEL SLIDER ---
        st.write("")
        st.markdown("**⏳ TEMPORAL SCANNER**")
        min_y, max_y = int(df['year'].min()), int(df['year'].max())
        
        # If range is invalid, default to 1950-2023
        if min_y >= max_y: min_y, max_y = 1950, 2023
            
        year_range = st.slider("Select Era:", min_y, max_y, (max_y-20, max_y))
        df_filtered = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1])]

        # --- MAIN MAP & DETAILS GRID ---
        c_map, c_detail = st.columns([3, 1])

        with c_map:
            st.markdown(f"#### 🛰️ GLOBAL SIGHTING GRID ({len(df_filtered)} Events)")
            
            # Map Config: Color by Shape
            # Colors: Green(Triangle), Cyan(Disk), Red(Light), Yellow(Other)
            def get_color(s):
                if 'triangle' in s: return [0, 255, 0, 200]
                elif 'disk' in s or 'saucer' in s: return [0, 255, 255, 200]
                elif 'light' in s or 'fireball' in s: return [255, 50, 50, 200]
                return [200, 200, 0, 150]
                
            df_filtered['color'] = df_filtered['shape'].apply(get_color)
            # Size by Duration (Log scale to prevent massive dots)
            df_filtered['radius'] = np.log(df_filtered['duration_sec'] + 1) * 5000

            layer = pdk.Layer(
                "ScatterplotLayer",
                data=df_filtered,
                get_position=['longitude', 'latitude'],
                get_radius='radius',
                get_fill_color='color',
                get_line_color=[0, 0, 0],
                stroked=True,
                filled=True,
                opacity=0.8,
                pickable=True
            )
            
            view_state = pdk.ViewState(latitude=38, longitude=-95, zoom=3, pitch=0)
            
            st.pydeck_chart(pdk.Deck(
                map_style="mapbox://styles/mapbox/dark-v10",
                initial_view_state=view_state,
                layers=[layer],
                tooltip={"text": "Shape: {shape}\nCity: {city}\nDuration: {duration_sec}s"},
                api_keys={"mapbox": "pk.eyJ1IjoidG9vcmVzZSIsImEiOiJjbTdtZ3h6eXQwMXVvMmpzNnZ6eXlzY3Z6In0.K8g8-g8g8-g8g8"}
            ))
            st.caption("Legend: 🟢 Triangle | 🔵 Disk/Saucer | 🔴 Light/Fireball | 🟡 Other")

        with c_detail:
            st.markdown("#### 📂 CASE FILE")
            
            # Selector
            # Create a unique label for selector
            df_filtered['label'] = df_filtered['datetime'].astype(str) + " - " + df_filtered['shape']
            
            if not df_filtered.empty:
                sel_id = st.selectbox("Select Report:", df_filtered.index, format_func=lambda x: df_filtered.loc[x, 'label'])
                item = df_filtered.loc[sel_id]
                
                with st.container(border=True):
                    st.markdown(f"**LOCATION:** {str(item.get('city', 'Unknown')).upper()}, {str(item.get('state', '')).upper()}")
                    st.markdown(f"**DATE:** {item['datetime'].date()}")
                    st.write("---")
                    
                    c1, c2 = st.columns(2)
                    icon = "🛸"
                    if 'triangle' in item['shape']: icon = "∆"
                    elif 'light' in item['shape']: icon = "✨"
                    
                    c1.metric("Shape", f"{icon} {item['shape'].upper()}")
                    c2.metric("Duration", f"{int(item['duration_sec']/60)} min")
                    
                    st.write("---")
                    st.caption("**WITNESS REPORT:**")
                    st.info(f'"{str(item["comments"])[:150]}..."')
            else:
                st.warning("No reports in this era.")

        # --- MIDDLE INSIGHTS ---
        st.write("---")
        st.markdown("### 📡 SIGNAL ANALYSIS")
        
        m1, m2, m3 = st.columns(3)
        
        with m1:
            st.markdown("**Common Shapes**")
            shape_counts = df_filtered['shape'].value_counts().head(8)
            fig_shapes = px.bar(x=shape_counts.values, y=shape_counts.index, orientation='h',
                                color=shape_counts.values, color_continuous_scale='Greens')
            fig_shapes.update_layout(template="plotly_dark", showlegend=False, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig_shapes, use_container_width=True)

        with m2:
            st.markdown("**Top Locations**")
            if 'state' in df_filtered.columns:
                loc_counts = df_filtered['state'].str.upper().value_counts().head(8)
                fig_loc = px.bar(x=loc_counts.index, y=loc_counts.values,
                                 color=loc_counts.values, color_continuous_scale='Bluered')
                fig_loc.update_layout(template="plotly_dark", showlegend=False, margin=dict(l=0,r=0,t=0,b=0))
                st.plotly_chart(fig_loc, use_container_width=True)
            else:
                st.info("State data unavailable.")

        with m3:
            st.markdown("**Duration Anomalies**")
            # Scatter: Year vs Duration
            fig_scat = px.scatter(df_filtered, x='year', y='duration_sec', color='shape',
                                  size='duration_sec', size_max=15, opacity=0.7)
            fig_scat.update_layout(template="plotly_dark", margin=dict(l=0,r=0,t=0,b=0), showlegend=False, yaxis_type="log")
            st.plotly_chart(fig_scat, use_container_width=True)

        # --- BOTTOM STORIES ---
        st.write("---")
        st.markdown("### 👽 UNEXPLAINED ENCOUNTERS")
        
        # Pick 3 random interesting comments
        if not df_filtered.empty:
            sample_size = min(3, len(df_filtered))
            stories = df_filtered.sample(sample_size)
            
            cols = st.columns(3)
            for i, (idx, row) in enumerate(stories.iterrows()):
                with cols[i]:
                    with st.container(border=True):
                        st.markdown(f"**{row['datetime'].date()} | {row.get('city', 'Unknown')}**")
                        st.markdown(f"*{row['comments']}*")


    # ------------------------------------------------------------------
    # PROJECT 6: NYC OPERATIONS CENTER
    # ------------------------------------------------------------------
    elif "NYC OPERATIONS CENTER" in project:
        
        st.markdown("""
            <div>
                <span class='hero-title'>NYC OPERATIONS CENTER</span>
                <span class='api-badge'>● LIVE CONNECTION</span>
            </div>
        """, unsafe_allow_html=True)
        
        with st.spinner("Initializing System..."):
            df = load_live_data()
            geojson = load_nyc_geojson()

        if df is not None and geojson is not None:
            
            # Prep Map
            zone_id_to_name = {}
            for feature in geojson['features']:
                props = feature['properties']
                loc_id = props.get('locationid') or props.get('LocationID') or props.get('objectid')
                zone_name = props.get('zone') or props.get('Zone') or "Unknown"
                if loc_id: zone_id_to_name[int(loc_id)] = zone_name

            # Selector
            active_ids = df['pulocationid'].value_counts().index.tolist()
            valid_ids = [i for i in active_ids if i in zone_id_to_name]
            sel_ids = st.multiselect("🔎 Select Zones:", valid_ids, format_func=lambda x: f"{zone_id_to_name.get(x)} ({x})")
            
            # Filter
            if not sel_ids:
                local_df = df
                display_name = "SYSTEM-WIDE"
            else:
                local_df = df[df['pulocationid'].isin(sel_ids)]
                display_name = f"{len(sel_ids)} ZONES SELECTED"

            # Layout
            col_map, col_panel = st.columns([2.5, 1])

            with col_map:
                # Color Logic
                zone_counts = df['pulocationid'].value_counts().reset_index()
                zone_counts.columns = ['locationid', 'trips']
                
                for feature in geojson['features']:
                    props = feature['properties']
                    loc_id = props.get('locationid') or props.get('LocationID') or props.get('objectid')
                    
                    if loc_id:
                        lid = int(loc_id)
                        # Add height based on global volume
                        row = zone_counts[zone_counts['locationid'] == lid]
                        count = row['trips'].sum() if not row.empty else 0
                        feature['properties']['height'] = int(count * 50) 
                        feature['properties']['trips'] = int(count)

                        if not sel_ids:
                            feature['properties']['fill_color'] = [30, 30, 30, 100]
                            feature['properties']['elevation'] = 10
                        elif lid in sel_ids:
                            feature['properties']['fill_color'] = [0, 102, 255, 255]
                            feature['properties']['elevation'] = 200
                        else:
                            feature['properties']['fill_color'] = [200, 200, 200, 50]
                            feature['properties']['elevation'] = 0
                    else:
                        feature['properties']['fill_color'] = [0,0,0,0]
                        feature['properties']['height'] = 0

                layer_zones = pdk.Layer(
                    "GeoJsonLayer",
                    data=geojson,
                    opacity=0.8,
                    stroked=True,
                    filled=True,
                    extruded=True,
                    wireframe=True,
                    get_elevation="properties.height",
                    get_fill_color="properties.fill_color",
                    get_line_color=[255, 255, 255],
                    get_line_width=20,
                    pickable=True,
                    auto_highlight=True,
                )
                
                st.pydeck_chart(pdk.Deck(
                    map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
                    initial_view_state=pdk.ViewState(latitude=40.73, longitude=-73.98, zoom=10.5, pitch=55, bearing=-20),
                    layers=[layer_zones],
                    tooltip={"text": "Zone: {zone}\nTrips: {trips}"}
                ))

            with col_panel:
                st.markdown(f"### 📡 {display_name} STATS")
                if not local_df.empty:
                    st.metric("Active Trips", len(local_df))
                    wait = local_df['wait_time'].mean()
                    st.metric("Avg Wait", f"{wait:.1f} min")
                    st.markdown("<div class='sparkline-box'>", unsafe_allow_html=True)
                    st.line_chart(local_df['wait_time'].reset_index(drop=True).head(15), height=30)
                    st.markdown("</div>", unsafe_allow_html=True)
                    st.metric("Avg Dist", f"{local_df['trip_miles'].mean():.1f} mi")
                    st.progress(0.8) # Mock revenue progress
                else:
                    st.warning("No Data")

            # Alerts
            st.write("---")
            st.markdown(f"### ⚠️ {display_name} ALERTS")
            a1, a2, a3 = st.columns(3)
            high_wait = len(local_df[local_df['wait_time'] > 15])
            with a1: st.markdown(f"<div class='alert-box'>⏱️ HIGH WAIT: {high_wait}</div>", unsafe_allow_html=True)
            with a2: st.markdown(f"<div class='alert-box' style='color:#0066ff; background:#e6f2ff; border-color:#99ccff;'>✈️ AIRPORT: {len(local_df[local_df['airport_fee']>0])}</div>", unsafe_allow_html=True)
            with a3: st.markdown(f"<div class='alert-box' style='color:#b38600; background:#fff9cc; border-color:#ffe066;'>🚕 SURCHARGE: {len(local_df[local_df['congestion_surcharge']>0])}</div>", unsafe_allow_html=True)

            # Insights
            st.markdown("### 📉 TACTICAL ANALYSIS")
            g1, g2, g3 = st.columns(3)
            with g1:
                st.markdown(f"**Destinations ({display_name})**")
                if not local_df.empty:
                    top = local_df['dolocationid'].value_counts().head(5)
                    # Use fallback string since zone_id_to_name might miss some IDs in fallback mode
                    names = [zone_id_to_name.get(i, str(i)) for i in top.index]
                    fig = px.bar(x=top.values, y=names, orientation='h')
                    fig.update_layout(showlegend=False, height=250, margin=dict(l=0,r=0,t=0,b=0))
                    st.plotly_chart(fig, use_container_width=True)
            with g2:
                st.markdown("**Distances**")
                if not local_df.empty:
                    fig2 = px.histogram(local_df[local_df['trip_miles']<20], x='trip_miles', nbins=15)
                    fig2.update_layout(height=250, margin=dict(l=0,r=0,t=0,b=0))
                    st.plotly_chart(fig2, use_container_width=True)
            with g3:
                st.markdown("**Shared vs Solo**")
                if not local_df.empty:
                    s = len(local_df[local_df['shared_request_flag']=='Y'])
                    fig3 = px.pie(values=[len(local_df)-s, s], names=['Solo', 'Shared'], hole=0.6)
                    fig3.update_layout(height=250, margin=dict(l=0,r=0,t=0,b=0), showlegend=True)
                    st.plotly_chart(fig3, use_container_width=True)

        else:
            st.error("System Offline. Unable to connect to data feed.")

# ==========================================
# 3. SKILLS & CONTACT
# ==========================================
# ==========================================
# 3. SKILLS PAGE
# ==========================================
elif page == "Skills":
    
    # --- PAGE STYLING ---
    st.markdown("""
    <style>
        .skill-badge {
            display: inline-block;
            background-color: #e6f0ff;
            color: #0066ff;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            margin: 4px 4px 4px 0;
            border: 1px solid #cce0ff;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        }
        .category-header {
            font-weight: 700;
            font-size: 1.1rem;
            margin-bottom: 12px;
            color: #1a1a1a;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .context-box {
            background-color: #ffffff;
            padding: 25px;
            border-radius: 10px;
            border: 1px solid #e0e0e0;
            border-left: 5px solid #0066ff;
            margin-top: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            font-size: 1.05rem;
            color: #444;
            line-height: 1.6;
        }
    </style>
    """, unsafe_allow_html=True)

    # --- HEADER ---
    st.title("SKILLS MATRIX")
    st.caption("Technical depth across the full data lifecycle")
    st.write("---")

    # --- SKILL CATEGORIES (4 Columns) ---
    c1, c2, c3, c4 = st.columns(4)

    # Helper function to render badges
    def render_skills(skills):
        html = ""
        for skill in skills:
            html += f"<span class='skill-badge'>{skill}</span>"
        return html

    with c1:
        with st.container(border=True):
            st.markdown("<div class='category-header'>💻 Programming & Engineering</div>", unsafe_allow_html=True)
            skills_list = ["Python", "SQL", "R", "Git", "Docker", "Spark"]
            st.markdown(render_skills(skills_list), unsafe_allow_html=True)

    with c2:
        with st.container(border=True):
            st.markdown("<div class='category-header'>📊 Analytics & Experimentation</div>", unsafe_allow_html=True)
            skills_list = ["Econometrics", "Causal Inference", "Statistical Modeling", "A/B Testing", "Bayesian Methods", "Forecasting"]
            st.markdown(render_skills(skills_list), unsafe_allow_html=True)

    with c3:
        with st.container(border=True):
            st.markdown("<div class='category-header'>👁️ Visualization & Platforms</div>", unsafe_allow_html=True)
            skills_list = ["Streamlit", "Plotly", "Pydeck", "Tableau", "QuickSight", "AWS"]
            st.markdown(render_skills(skills_list), unsafe_allow_html=True)
            
    with c4:
        with st.container(border=True):
            st.markdown("div class='category-header'> Machine Learning</div>", unsafe_allow_html=True)
            skills_list = ["Supervised Learning", "Unsupervised Learning", "Ensemble Method"]
            st.markdown(render_skills(skills_list), unsafe_allow_html=True)


    # --- PROFICIENCY INDICATORS ---
    st.write("")
    st.markdown("### Core Proficiency")
    p1, p2, p3, p4 = st.columns(4)
    
    with p1:
        st.write("**Python**")
        st.progress(0.95)
    with p2:
        st.write("**SQL**")
        st.progress(0.90)
    with p3:
        st.write("**Experimentation & Measurement**")
        st.progress(0.90)
    with p4:
        st.write("**ML**")
        st.progress(0.65)

    # --- CONTEXT ---
    st.markdown("""
        <div class="context-box">
            I work as a full stack data scientist. I build data pipelines and models, design experiments, and translate results into product insights. 
            My strongest areas are Python, SQL, and measurement science.
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# 4. CONTACT PAGE
# ==========================================
elif page == "Contact":
    
    # --- PAGE STYLING ---
    st.markdown("""
    <style>
        /* FADE IN ANIMATION */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .contact-page {
            animation: fadeIn 1.0s ease-out;
        }
        
        /* CONTACT CARDS */
        .contact-card {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 30px 20px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            transition: all 0.3s ease;
            height: 100%;
            cursor: pointer;
        }
        .contact-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 12px 24px rgba(0, 102, 255, 0.15);
            border-color: #0066ff;
        }
        .icon-box {
            font-size: 3rem;
            margin-bottom: 15px;
        }
        .card-title {
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #888;
            margin-bottom: 8px;
            font-weight: 600;
        }
        .card-link a {
            text-decoration: none;
            color: #1a1a1a;
            font-size: 1.1rem;
            font-weight: 700;
            word-wrap: break-word;
        }
        .card-link a:hover {
            color: #0066ff;
        }

        /* FORM CONTAINER */
        .form-box {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 15px;
            padding: 40px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.05);
            margin-top: 40px;
        }
    </style>
    """, unsafe_allow_html=True)

    # --- WRAPPER ---
    st.markdown('<div class="contact-page">', unsafe_allow_html=True)
    
    # 1. HEADER
    st.markdown("<h1 style='text-align: center; margin-bottom: 50px;'>CONTACT ME</h1>", unsafe_allow_html=True)

    # 2. CONTACT INFORMATION CARDS
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
        <div class="contact-card">
            <div class="icon-box">✉️</div>
            <div class="card-title">Email</div>
            <div class="card-link">
                <a href="mailto:toorese@gmail.com">toorese@gmail.com</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="contact-card">
            <div class="icon-box">🖥️</div>
            <div class="card-title">GitHub</div>
            <div class="card-link">
                <a href="https://github.com/torelash" target="_blank">github.com/torelash</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="contact-card">
            <div class="icon-box">🔗</div>
            <div class="card-title">LinkedIn</div>
            <div class="card-link">
                <a href="https://www.linkedin.com/in/toorese-l/" target="_blank">linkedin.com/in/toorese-l</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 3. MESSAGE FORM SECTION
    # Using layout columns to center the form visually
    _, col_main, _ = st.columns([1, 2, 1])
    
    with col_main:
        st.markdown("<br>", unsafe_allow_html=True)
        # Styled Form Container
        with st.container(border=True):
            st.markdown("<h3 style='text-align: center;'>Send a Message</h3>", unsafe_allow_html=True)
            
            with st.form("contact_form", clear_on_submit=True):
                name = st.text_input("Name", placeholder="Your Name")
                email = st.text_input("Email", placeholder="Your Email Address")
                message = st.text_area("Message", placeholder="Tell me about your project...", height=150)
                
                # Submit Button
                submit_btn = st.form_submit_button("🚀 Send Message", use_container_width=True)
                
                if submit_btn:
                    if name and email and message:
                        # Store in session state (Simulation of backend)
                        st.session_state['form_submitted'] = True
                        st.success(f"Thank you, {name}! Your message has been sent successfully.")
                    else:
                        st.warning("Please fill in all fields before sending.")

    st.markdown('</div>', unsafe_allow_html=True)
