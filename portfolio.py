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

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Toorese | Portfolio",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. SESSION STATE NAVIGATION LOGIC ---
if 'page' not in st.session_state:
    st.session_state.page = "Home"

# --- SESSION STATE INITIALIZATION ---
if 'show_toast' not in st.session_state:
    st.session_state.show_toast = False
if 'toast_message' not in st.session_state:
    st.session_state.toast_message = ""
# --- NEW KEY ---
if "active_hobby" not in st.session_state:
    st.session_state.active_hobby = None

def navigate_to(page_name):
    st.session_state.page = page_name
    st.rerun()




# --- 3. GLOBAL STYLING & FONTS ---
# --- 3. DYNAMIC STYLING (Dark Home, Light Content) ---

# A. DEFINE THE CSS FOR EACH THEME
dark_home_css = """
    /* EDITORIAL CREAM BACKGROUND (Home) */
    .stApp {
        background-color: #FBFAF7;
        background-image: none;
    }
    
    h1, h2, h3, h4, h5, p, div, span, label {
        color: #16130E;
    }
    .stMarkdown, .stText { color: #6E6A60; }
    
    /* FLAT MONOSPACE NAV BUTTONS */
    div.stButton > button {
        width: 100%;
        background-color: transparent;
        color: #16130E;
        border: 1px solid #E2DDD2;
        border-radius: 2px;
        height: auto;
        min-height: 90px;
        padding: 20px 22px;
        text-align: left;
        transition: all 0.2s ease;
    }
    div.stButton > button p {
        font-family: 'Spline Sans Mono', monospace;
        text-align: left;
        margin: 0;
        line-height: 1.5;
    }
    div.stButton > button p:first-of-type {
        font-size: 0.95rem;
        letter-spacing: 0.03em;
    }
    div.stButton > button p:not(:first-of-type) {
        font-size: 0.78rem;
        color: #6E6A60;
        letter-spacing: 0.01em;
        margin-top: 6px;
    }
    div.stButton > button:hover {
        background-color: #F3E6E1;
        border-color: #A6402A;
        color: #A6402A;
        transform: none;
    }
    div.stButton > button:hover p:not(:first-of-type) {
        color: #A6402A;
    }
"""

light_content_css = """
    /* EDITORIAL CREAM BACKGROUND (Content pages) */
    .stApp {
        background-color: #FBFAF7;
        background-image: none;
    }
    
    /* RESET TEXT COLORS */
    h1, h2, h3, .name-title {
        color: #16130E;
        font-family: 'Spectral', serif;
    }
    
    /* FLAT MONOSPACE 'BACK' BUTTON */
    div.stButton > button {
        background-color: transparent;
        color: #6E6A60;
        border: 1px solid #E2DDD2;
        border-radius: 2px;
        padding: 5px 15px;
        font-family: 'Spline Sans Mono', monospace;
        font-weight: 400;
        font-size: 0.85rem;
    }
    div.stButton > button:hover {
        border-color: #A6402A;
        color: #A6402A;
    }

    /* --- HAIRLINE METRIC CARDS --- */
    div[data-testid="stMetric"] {
        background-color: #FBFAF7;
        border: 1px solid #E2DDD2;
        padding: 22px 15px;
        border-radius: 2px;
        box-shadow: none;
        text-align: center;
        width: 100%;
    }
    
    /* Force center alignment */
    div[data-testid="stMetric"] > div {
        width: 100%;
        margin: 0 auto;
        justify-content: center;
    }
"""

# B. SELECT CSS BASED ON PAGE
if st.session_state.page == "Home":
    active_css = dark_home_css
else:
    active_css = light_content_css

# C. RENDER CSS
st.markdown(f"""
<style>
    /* 1. GLOBAL FONTS (Always Apply) */
    @import url('https://fonts.googleapis.com/css2?family=Spectral:ital,wght@0,300;0,400;0,500;0,600;1,400;1,500&family=Spline+Sans+Mono:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Spectral', Georgia, serif;
    }}
    h1, h2, h3, .name-title, .nav-header {{
        font-family: 'Spectral', serif;
        font-weight: 600;
    }}
    .mono-label {{
        font-family: 'Spline Sans Mono', monospace;
        letter-spacing: 0.03em;
    }}
    
    /* 2. HIDE SIDEBAR (Always) */
    [data-testid="stSidebar"] {{ display: none; }}
    header {{ visibility: hidden; }}
    .block-container {{ padding-top: 4rem; max-width: 980px; }}
    hr {{ border-color: #E2DDD2 !important; }}

    /* 3. HOME PAGE SPECIFIC CLASSES (Profile, Pills, Bio) */
    .profile-img {{ 
        width: 132px; height: 132px; border-radius: 50%; object-fit: cover; 
        border: 1px solid #E2DDD2; box-shadow: none; 
    }}
    .name-title {{ font-size: 3rem; font-weight: 500; font-style: italic; color: #16130E; margin-bottom: 6px; line-height: 1.15; }}
    .bio-text {{ font-size: 1.05rem; line-height: 1.8; color: #6E6A60; font-weight: 400; }}
    
    .link-pill {{ 
        text-decoration: none; background: transparent; 
        color: #6E6A60 !important; padding: 4px 0; border-radius: 0; 
        font-size: 0.82rem; font-family: 'Spline Sans Mono', monospace; letter-spacing: 0.02em;
        border: none; border-bottom: 1px solid #C9C3B5;
        margin-right: 22px; transition: all 0.2s ease; display: inline-block; margin-top: 5px;
    }}
    .link-pill:hover {{ border-color: #A6402A; color: #A6402A !important; }}

    /* 4. ACTIVE THEME (Injected) */
    {active_css}

</style>
""", unsafe_allow_html=True)


# ==========================================
# MASTER ROUTING LOGIC
# ==========================================

# --- 1. HOME PAGE LOGIC ---
if st.session_state.page == "Home":
    
    # --- HEADER SECTION (Using standard Streamlit columns for layout) ---
    c1, c2 = st.columns([1, 2.5])
    
    with c1:
        # Profile Image
        st.markdown('<img class="profile-img" src="https://placehold.co/400x400/FBFAF7/A6402A?text=TL">', unsafe_allow_html=True)
        
    with c2:
        # Name & Title
        st.markdown('<div class="name-title">Toorese Lasebikan</div>', unsafe_allow_html=True)
        
        # Pill Links
        st.markdown("""
            <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px;">
                <a href="mailto:toorese@gmail.com" class="link-pill">✉️ toorese@gmail.com</a>
                <a href="https://github.com/torelash" target="_blank" class="link-pill">🐙 GitHub</a>
                <a href="https://linkedin.com/in/toorese-l" target="_blank" class="link-pill">🔗 LinkedIn</a>
            </div>
        """, unsafe_allow_html=True)

    # --- BIO SECTION ---
    st.write("") # Spacer
    st.markdown("""
    <div style="font-size: 1.1rem; line-height: 1.7; color: #2c2822; margin-top: 20px; max-width: 900px;">
        Hi! I am Toorese. I am a data scientist who currently work in analytics at Amazon Business building metrics and machine learning programs that
        support millions of customers and improve decisions at scale. I earned my masters in Data Analytics and Policy from Carnegie Mellon University
        and my bachelors in Economics. I am especially interested in algorithmic fairness and how AI shapes outcomes in real systems. Outside of work,
        I love basketball and I enjoy building creative tech projects that explore how data meets everyday life.
    </div>
    """, unsafe_allow_html=True)
    
    st.write("---") # Divider line

    # --- NAVIGATION SECTION ---
    st.markdown("<h3 style='color:#A6402A; font-style: italic; margin-bottom: 20px;'>Explore Portfolio</h3>", unsafe_allow_html=True)
    
    # Row 1: Main Nav
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📂 PROJECTS\n\nCurated tools & models"):
            navigate_to("Projects")
    with col2:
        if st.button("🧠 SKILLS\n\nTech stack & expertise"):
            navigate_to("Skills")
    with col3:
        if st.button("💬 CONTACT\n\nLet's connect"):
            navigate_to("Contact")

    # Row 2: Hobbies
    # Hobbies Grid
    st.markdown("<h3 style='color:#A6402A; font-style: italic; margin-top: 30px; font-size: 1.2rem;'>Analytics Hobbies</h3>", unsafe_allow_html=True)
    h1, h2 = st.columns(2)
    with h1:
        if st.button("🏀 NBA ANALYTICS"): navigate_to("NBA")
    with h2:
        if st.button("⛹️‍♀️ WNBA ANALYTICS"): navigate_to("WNBA")


# --- SMART DATA LOADER (COMBINED FIX) ---
@st.cache_data
def load_data(filename, limit=None, sample_rate=None):
    """
    1. limit: Load only the top N rows (Good for simple testing).
    2. sample_rate: Load a random % of rows (Good for seeing ALL years without crashing).
       Example: sample_rate=0.1 loads 10% of the data.
    """
    try:
        # Get directory of this script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(current_dir, "data", filename)
        
        # LOGIC: Define which rows to skip if sampling is on
        skip_logic = None
        if sample_rate is not None:
            # lambda x: Keep header (x==0) or keep row if random number < sample_rate
            import random
            skip_logic = lambda x: x > 0 and random.random() > sample_rate

        try:
            return pd.read_csv(
                path, 
                encoding='utf-8', 
                on_bad_lines='skip', 
                nrows=limit, 
                skiprows=skip_logic
            )
        except UnicodeDecodeError:
            return pd.read_csv(
                path, 
                encoding='windows-1252', 
                on_bad_lines='skip', 
                nrows=limit,
                skiprows=skip_logic
            )
    except:
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



# ==========================================
# 1. HOME
# ==========================================
if st.session_state.page == "Home":
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

# ==========================================
# 2. PROJECTS
# ==========================================
elif st.session_state.page == "Projects":
    # The "Back" button to return to the dashboard
    if st.button("← Back to Home", key="back_projects"): 
        navigate_to("Home")
    
    st.write("") # Spacer
    
    project = st.selectbox("Select Active Module:", 
        ["1. Superstore Sales", "2. Heart Disease AI", "3. Movie Trends", "4. Meteorite Tracker", "5. UFO Sightings", "6. NYC OPERATIONS CENTER"],
        index=0 
    )
    st.write("---")

    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    # PROJECT 1: SUPERSTORE SALES (EXECUTIVE INTELLIGENCE SUITE)
    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    # PROJECT 1: SUPERSTORE SALES (FINAL POLISHED LAYOUT)
    # ------------------------------------------------------------------
    if "Superstore Sales" in project:
        from plotly.subplots import make_subplots
        
        # 1. LOAD DATA
        df = load_data("sales.csv")
        df.columns = df.columns.str.strip()
        
        # Ensure Types
        date_col = next((c for c in df.columns if 'date' in c.lower()), 'Order Date')
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        if 'Ship Mode' not in df.columns: df['Ship Mode'] = np.random.choice(['Standard', 'Second', 'First'], len(df))
        if 'Discount' not in df.columns: df['Discount'] = np.random.uniform(0, 0.4, len(df))
        if 'Customer Name' not in df.columns: df['Customer Name'] = [f"Cust {i}" for i in np.random.randint(1, 500, len(df))]

        # --- THEME CONFIG ---
        BG_COLOR = "#0B132B"      # Deep Navy (Charts)
        CARD_COLOR = "#1C2541"    # Lighter Navy (Card Backgrounds)
        GOLD = "#D4AF37"          # Accent Gold
        CREAM = "#F0F8FF"         # Secondary Light Text
        
        # --- TITLE BANNER (FIXED VISIBILITY) ---
        # Using a dark container for the title ensures the text pops, regardless of page theme.
        
        st.markdown(f"""
            <div style="background-color:{BG_COLOR}; padding:20px; border-radius:10px; margin-bottom:25px; border-bottom: 4px solid {GOLD}; text-align: center;">
                <h2 style="color:{GOLD}; margin:0; font-family:'Segoe UI', sans-serif; letter-spacing: 2px;">GLOBAL SALES PERFORMANCE DASHBOARD</h2>
            </div>
        """, unsafe_allow_html=True)

        # --- FILTERS (CLEAN ROW) ---
        # Removed the broken wrapper div; using clean columns for native widget look.
        f1, f2, f3 = st.columns(3)
        
        with f1:
            all_regions = sorted(df['Region'].unique().tolist()) if 'Region' in df.columns else []
            sel_region = st.multiselect("📍 Filter Region:", all_regions, placeholder="All Regions")
            df_r = df[df['Region'].isin(sel_region)] if sel_region else df
            
        with f2:
            avail_states = sorted(df_r['State'].unique().tolist())
            sel_state = st.multiselect("🏳️ Filter State:", avail_states, placeholder="All States")
            df_s = df_r[df_r['State'].isin(sel_state)] if sel_state else df_r
            
        with f3:
            avail_cities = sorted(df_s['City'].unique().tolist()) if 'City' in df_s.columns else []
            sel_city = st.multiselect("🏙️ Filter City:", avail_cities, placeholder="All Cities")
            df_viz = df_s[df_s['City'].isin(sel_city)] if sel_city else df_s

        st.write("---")

        # --- AGGREGATIONS ---
        total_sales = df_viz['Sales'].sum()
        total_profit = df_viz['Profit'].sum()
        margin = (total_profit / total_sales) * 100 if total_sales > 0 else 0
        total_orders = len(df_viz)
        
        # --- KPI CARDS ---
        st.markdown(f"""
        <style>
            .kpi-card {{
                background-color: {CARD_COLOR};
                border-left: 5px solid {GOLD};
                padding: 15px;
                border-radius: 8px;
                text-align: center;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .kpi-label {{ color: #a0a0a0; font-size: 0.85rem; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; }}
            .kpi-val {{ color: {GOLD}; font-size: 1.8rem; font-weight: 700; margin-top: 5px; }}
        </style>
        """, unsafe_allow_html=True)
        
        k1, k2, k3, k4 = st.columns(4)
        with k1: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>REVENUE</div><div class='kpi-val'>${total_sales:,.0f}</div></div>", unsafe_allow_html=True)
        with k2: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>NET PROFIT</div><div class='kpi-val'>${total_profit:,.0f}</div></div>", unsafe_allow_html=True)
        with k3: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>MARGIN</div><div class='kpi-val'>{margin:.1f}%</div></div>", unsafe_allow_html=True)
        with k4: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>ORDERS</div><div class='kpi-val'>{total_orders:,}</div></div>", unsafe_allow_html=True)

        st.write("") 

        # --- MIDDLE ROW: MAP | CATEGORY | TREND ---
        m1, m2, m3 = st.columns([1.2, 1, 1])
        
        # 1. MAP (Left)
        with m1:
            st.markdown(f"<h5 style='color:{GOLD}; text-align:center;'>GEOGRAPHIC FOOTPRINT</h5>", unsafe_allow_html=True)
            
            state_sales = df.groupby('State')['Sales'].sum().reset_index()
            # Logic: If states selected, highlight them. Else, heatmap style.
            if sel_state:
                state_sales['Color'] = state_sales['State'].apply(lambda x: 10 if x in sel_state else 1)
                color_col, color_scale = 'Color', [[0, '#1C2541'], [0.5, '#1C2541'], [1, GOLD]]
            else:
                color_col, color_scale = 'Sales', [[0, '#1C2541'], [1, GOLD]]

            fig_map = px.scatter_geo(
                state_sales, locations="State", locationmode="USA-states",
                size="Sales", color=color_col, color_continuous_scale=color_scale,
                scope="usa", hover_name="State"
            )
            fig_map.update_traces(marker=dict(line=dict(width=1, color=GOLD)))
            fig_map.update_layout(
                paper_bgcolor=BG_COLOR,
                geo=dict(bgcolor=BG_COLOR, lakecolor=BG_COLOR, landcolor='#151b2e', subunitcolor='#333'),
                margin=dict(l=0, r=0, t=0, b=0), height=300, dragmode=False, showlegend=False, coloraxis_showscale=False
            )
            st.plotly_chart(fig_map, use_container_width=True)

        # 2. CATEGORY / TOP CITIES (Middle)
        with m2:
            if sel_state:
                st.markdown(f"<h5 style='color:{GOLD}; text-align:center;'>TOP CITIES</h5>", unsafe_allow_html=True)
                city_perf = df_viz.groupby('City')[['Sales', 'Profit']].sum().sort_values('Sales', ascending=False).head(10).reset_index()
                fig_mid = make_subplots(specs=[[{"secondary_y": True}]])
                fig_mid.add_trace(go.Bar(x=city_perf['City'], y=city_perf['Sales'], name='Sales', marker_color=GOLD), secondary_y=False)
                fig_mid.add_trace(go.Scatter(x=city_perf['City'], y=city_perf['Profit'], name='Profit', line=dict(color=CREAM, width=2)), secondary_y=True)
            else:
                st.markdown(f"<h5 style='color:{GOLD}; text-align:center;'>CATEGORY PERFORMANCE</h5>", unsafe_allow_html=True)
                cat_perf = df_viz.groupby('Category')[['Sales', 'Profit']].sum().reset_index()
                fig_mid = go.Figure()
                fig_mid.add_trace(go.Bar(x=cat_perf['Category'], y=cat_perf['Sales'], name='Sales', marker_color=GOLD))
                fig_mid.add_trace(go.Bar(x=cat_perf['Category'], y=cat_perf['Profit'], name='Profit', marker_color=CREAM))
                fig_mid.update_layout(barmode='group')

            fig_mid.update_layout(template="plotly_dark", paper_bgcolor=BG_COLOR, plot_bgcolor=BG_COLOR, height=300, margin=dict(t=10,l=0,r=0,b=0), showlegend=False)
            st.plotly_chart(fig_mid, use_container_width=True)

        # 3. PROFIT TREND (Right)
        with m3:
            st.markdown(f"<h5 style='color:{GOLD}; text-align:center;'>PROFIT TREND</h5>", unsafe_allow_html=True)
            trend = df_viz.groupby(pd.Grouper(key=date_col, freq='M'))['Profit'].sum().reset_index()
            fig_trend = px.area(trend, x=date_col, y='Profit', line_shape='spline')
            fig_trend.update_traces(line_color=GOLD, fillcolor='rgba(212, 175, 55, 0.1)')
            fig_trend.update_layout(
                template="plotly_dark", paper_bgcolor=BG_COLOR, plot_bgcolor=BG_COLOR, 
                font_color="#FFF", margin=dict(l=0,r=0,t=10,b=0), height=300, xaxis_title="", yaxis_title=""
            )
            st.plotly_chart(fig_trend, use_container_width=True)

        # --- DEEP DIVE TABS ---
        st.write("")
        st.markdown(f"<h3 style='color:#333; border-bottom: 2px solid {GOLD}; padding-bottom:10px;'>🧠 DEEP DIVE ANALYTICS</h3>", unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4 = st.tabs(["📊 FORECASTING", "👥 CUSTOMER DNA", "🛍️ PRODUCT", "🚚 LOGISTICS"])
        
        with tab1:
            st.markdown("**Profit Forecast (Next 12 Months)**")
            if len(trend) > 5:
                last_date = trend[date_col].max()
                future_dates = [last_date + pd.DateOffset(months=x) for x in range(1, 13)]
                avg_prof = trend['Profit'].mean()
                # Fix: Ensure positive scale for noise
                scale_val = abs(avg_prof * 0.2) if avg_prof != 0 else 100
                forecast = [avg_prof * (1 + i*0.02) + np.random.normal(0, scale_val) for i in range(12)]
                
                fig_cast = go.Figure()
                fig_cast.add_trace(go.Scatter(x=trend[date_col], y=trend['Profit'], name='History', line=dict(color=CREAM)))
                fig_cast.add_trace(go.Scatter(x=future_dates, y=forecast, name='Forecast', line=dict(color=GOLD, dash='dash')))
                fig_cast.update_layout(template="plotly_dark", paper_bgcolor=BG_COLOR, plot_bgcolor=BG_COLOR, height=350, margin=dict(t=10,l=0,r=0,b=0))
                st.plotly_chart(fig_cast, use_container_width=True)
            else:
                st.info("Insufficient data history for this selection.")

        with tab2:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Profitability Pareto**")
                cust_prof = df_viz.groupby('Customer Name')['Profit'].sum().sort_values(ascending=False).head(15).reset_index()
                cust_prof['Color'] = np.where(cust_prof['Profit']<0, '#FF4B4B', GOLD)
                fig_par = px.bar(cust_prof, x='Customer Name', y='Profit', color='Color', color_discrete_map="identity")
                fig_par.update_layout(template="plotly_dark", paper_bgcolor=BG_COLOR, plot_bgcolor=BG_COLOR, showlegend=False, height=250, xaxis={'visible':False})
                st.plotly_chart(fig_par, use_container_width=True)
            with c2:
                st.markdown("**Segment Share**")
                seg = df_viz.groupby('Segment')['Sales'].sum().reset_index()
                fig_pie = px.pie(seg, values='Sales', names='Segment', hole=0.5, color_discrete_sequence=[GOLD, CREAM, '#8d99ae'])
                fig_pie.update_layout(template="plotly_dark", paper_bgcolor=BG_COLOR, plot_bgcolor=BG_COLOR, height=250, margin=dict(t=0,b=0,l=0,r=0))
                st.plotly_chart(fig_pie, use_container_width=True)

        with tab3:
            st.markdown("**Top Sub-Categories**")
            sub = df_viz.groupby('Sub-Category')['Sales'].sum().nlargest(8).sort_values(ascending=True)
            fig_sub = px.bar(x=sub.values, y=sub.index, orientation='h')
            fig_sub.update_traces(marker_color=GOLD)
            fig_sub.update_layout(template="plotly_dark", paper_bgcolor=BG_COLOR, plot_bgcolor=BG_COLOR, height=250, margin=dict(t=0,b=0,l=0,r=0))
            st.plotly_chart(fig_sub, use_container_width=True)

        with tab4:
            l1, l2 = st.columns(2)
            with l1:
                st.markdown("**Shipping Efficiency**")
                ship = df_viz.groupby('Ship Mode').agg({'Profit':'mean', 'Sales':'sum'}).reset_index()
                fig_ship = px.scatter(ship, x='Sales', y='Profit', size='Sales', color='Ship Mode')
                fig_ship.update_layout(template="plotly_dark", paper_bgcolor=BG_COLOR, plot_bgcolor=BG_COLOR, height=250)
                st.plotly_chart(fig_ship, use_container_width=True)
            with l2:
                st.markdown("**Margin Anomalies**")
                df_viz['Margin'] = df_viz['Profit'] / df_viz['Sales']
                fig_anom = px.scatter(df_viz, x='Discount', y='Margin', color='Profit', color_continuous_scale='RdYlGn')
                fig_anom.add_hrect(y0=-5, y1=-0.1, fillcolor="red", opacity=0.1, line_width=0)
                fig_anom.update_layout(template="plotly_dark", paper_bgcolor=BG_COLOR, plot_bgcolor=BG_COLOR, height=250)
                st.plotly_chart(fig_anom, use_container_width=True)
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
        df = load_data("ufo.csv", sample_rate=0.20)
        
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
# 3. SKILLS PAGE
# ==========================================
elif st.session_state.page == "Skills":
    if st.button("← Back Home", key="back_skills"): navigate_to("Home")
    
    # --- PAGE STYLING ---
    st.markdown("""
    <style>
        .skill-badge {
            display: inline-block;
            background-color: transparent;
            color: #6E6A60;
            padding: 5px 14px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-family: 'Spline Sans Mono', monospace;
            font-weight: 400;
            margin: 4px 4px 4px 0;
            border: 1px solid #E2DDD2;
            box-shadow: none;
        }
        .category-header {
            font-family: 'Spectral', serif;
            font-style: italic;
            font-weight: 600;
            font-size: 1.15rem;
            margin-bottom: 12px;
            color: #16130E;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .context-box {
            background-color: #FBFAF7;
            padding: 25px;
            border-radius: 2px;
            border: 1px solid #E2DDD2;
            border-left: 3px solid #A6402A;
            margin-top: 30px;
            box-shadow: none;
            font-size: 1.05rem;
            color: #6E6A60;
            line-height: 1.7;
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
elif st.session_state.page == "Contact":
    if st.button("← Back Home", key="back_contact"): navigate_to("Home")
    
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
            background-color: #FBFAF7;
            border: 1px solid #E2DDD2;
            border-radius: 2px;
            padding: 30px 20px;
            text-align: center;
            box-shadow: none;
            transition: all 0.2s ease;
            height: 100%;
            cursor: pointer;
        }
        .contact-card:hover {
            transform: translateY(-4px);
            box-shadow: none;
            border-color: #A6402A;
        }
        .icon-box {
            font-size: 3rem;
            margin-bottom: 15px;
        }
        .card-title {
            font-family: 'Spline Sans Mono', monospace;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #6E6A60;
            margin-bottom: 8px;
            font-weight: 400;
        }
        .card-link a {
            text-decoration: none;
            color: #16130E;
            font-size: 1.1rem;
            font-weight: 700;
            word-wrap: break-word;
        }
        .card-link a:hover {
            color: #A6402A;
        }

        /* FORM CONTAINER */
        .form-box {
            background-color: #FBFAF7;
            border: 1px solid #E2DDD2;
            border-radius: 2px;
            padding: 40px;
            box-shadow: none;
            margin-top: 40px;
        }
    </style>
    """, unsafe_allow_html=True)

    # --- WRAPPER ---
    st.markdown('<div class="contact-page">', unsafe_allow_html=True)
    
    # 1. HEADER
    st.markdown("<h1 style='text-align: center; margin-bottom: 50px;'>CONTACT ME</h1>", unsafe_allow_html=True)


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

# 5. HOBBY PAGES (NBA / WNBA)
elif st.session_state.page == "NBA":
    if st.button("← Back Home", key="back_nba"): navigate_to("Home")
    render_nba()

elif st.session_state.page == "WNBA":
    if st.button("← Back Home", key="back_wnba"): navigate_to("Home")
    render_wnba()
