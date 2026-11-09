import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. Page Configuration & Title
st.set_page_config(page_title="Nifty MidSmall 400 Breadth", layout="wide")
st.title("📈 Nifty MidSmallcap 400 Breadth Dashboard")
st.markdown("### Date-wise % of Stocks Trading Above EMAs (2x2 Matrix Layout)")
st.markdown("---")

# Sidebar Filters
st.sidebar.header("🎯 Dashboard Controls & Filters")

# 2. Index Selection
market_type = st.sidebar.selectbox("Select Index Market:", ["Nifty MidSmall 400 (Top Actionable)", "Nifty 50"])

MIDSML_400_TICKERS = [
    'LICHSGFIN.NS', 'BHEL.NS', 'RECLTD.NS', 'PFC.NS', 'OIL.NS', 'GICRE.NS', 'IDBI.NS',
    'BANKMAHA.NS', 'NMDC.NS', 'NATIONALUM.NS', 'YESBANK.NS', 'HAVELLS.NS', 'KALYANKJIL.NS', 
    'MCX.NS', 'CROMPTON.NS', 'GLENMARK.NS', 'STARHEALTH.NS', 'CARTRADE.NS', 'ACE.NS', 
    'IIFL.NS', 'FORCEMOT.NS', 'CHOLAFIN.NS', 'KARURVYSYA.NS', 'ICICIPRULI.NS', 'JMFINANCE.NS',
    'SHYAMMETL.NS', 'BSOFT.NS', 'POONAWALLA.NS', 'JSWENERGY.NS', 'IRFC.NS', 'RVNL.NS',
    'HUDCO.NS', 'SAIL.NS', 'UNIONBANK.NS', 'CENTRALBK.NS', 'IOB.NS', 'ZOMATO.NS', 'JIOFIN.NS'
]

NIFTY_50_TICKERS = [
    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'BHARTIARTL.NS', 'ICICIBANK.NS', 'INFY.NS', 'SBI.NS', 'ITC.NS'
]

TICKERS = MIDSML_400_TICKERS if "MidSmall" in market_type else NIFTY_50_TICKERS

# 3. Date Filters
max_end_date = datetime.today()
default_start = max_end_date - timedelta(days=365)

st.sidebar.subheader("📅 Select Custom Date Range")
start_filter = st.sidebar.date_input("Start Date", default_start)
end_filter = st.sidebar.date_input("End Date", max_end_date)

def calculate_ema(series, length):
    return series.ewm(span=length, adjust=False).mean()

@st.cache_data(ttl=3600)
def get_upgraded_breadth_data(market_name):
    selected_tickers = MIDSML_400_TICKERS if "MidSmall" in market_name else NIFTY_50_TICKERS
    end_date = datetime.today()
    start_date = end_date - timedelta(days=550) 
    
    flat_records = list()
    progress_bar = st.progress(0)
    
    for i, ticker in enumerate(selected_tickers):
        try:
            df = yf.Ticker(ticker).history(start=start_date, end=end_date, auto_adjust=True)
            if not df.empty and len(df) >= 200:
                df['EMA_10'] = calculate_ema(df['Close'], 10)
                df['EMA_20'] = calculate_ema(df['Close'], 20)
                df['EMA_50'] = calculate_ema(df['Close'], 50)
                df['EMA_200'] = calculate_ema(df['Close'], 200)
                
                for date, row in df.iterrows():
                    flat_records.append({
                        'Date': date.strftime('%Y-%m-%d'),
                        'Ticker': ticker,
                        'Above_10': 1 if row['Close'] > row['EMA_10'] else 0,
                        'Above_20': 1 if row['Close'] > row['EMA_20'] else 0,
                        'Above_50': 1 if row['Close'] > row['EMA_50'] else 0,
                        'Above_200': 1 if row['Close'] > row['EMA_200'] else 0
                    })
        except Exception:
            continue
        progress_bar.progress((i + 1) / len(selected_tickers))
        
    progress_bar.empty()
    if not flat_records:
        return pd.DataFrame()
        
    master_df = pd.DataFrame(flat_records)
    grouped = master_df.groupby('Date').agg(
        Total_Active=('Ticker', 'count'),
        A10=('Above_10', 'sum'),
        A20=('Above_20', 'sum'),
        A50=('Above_50', 'sum'),
        A200=('Above_200', 'sum')
    ).reset_index()
    
    grouped['10 EMA'] = round((grouped['A10'] / grouped['Total_Active']) * 100, 2)
    grouped['20 EMA'] = round((grouped['A20'] / grouped['Total_Active']) * 100, 2)
    grouped['50 EMA'] = round((grouped['A50'] / grouped['Total_Active']) * 100, 2)
    grouped['200 EMA'] = round((grouped['A200'] / grouped['Total_Active']) * 100, 2)
    
    return grouped[['Date', '10 EMA', '20 EMA', '50 EMA', '200 EMA']]

# Run Calculation
with st.spinner(f"Downloading data for {market_type} constituents..."):
    df_breadth_raw = get_upgraded_breadth_data(market_type)

# Helper function to generate single clean plot
def create_individual_plot(df, column_name, color):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['Date'], y=df[column_name],
        mode='lines', name=column_name,
        line=dict(color=color, width=2)
    ))
    fig.update_layout(
        title=dict(text=f"<b>{column_name} Breadth Overview</b>", font=dict(size=15)),
        xaxis_title="Date",
        yaxis_title="% Stocks Above",
        yaxis=dict(range=[0, 105]),
        hovermode="x unified",
        template="plotly_white",
        margin=dict(l=20, r=20, t=40, b=20),
        height=320
    )
    return fig

if not df_breadth_raw.empty:
    df_breadth_raw['Date_Parsed'] = pd.to_datetime(df_breadth_raw['Date'])
    mask = (df_breadth_raw['Date_Parsed'].dt.date >= start_filter) & (df_breadth_raw['Date_Parsed'].dt.date <= end_filter)
    df_breadth = df_breadth_raw.loc[mask].copy()

    if not df_breadth.empty:
        colors = {'10 EMA': '#e74c3c', '20 EMA': '#e67e22', '50 EMA': '#f1c40f', '200 EMA': '#2ecc71'}
        
        # 🚀 2x2 Matrix layout allocation
        st.markdown("### 📊 Market Breadth Grids")
        
        # ROW 1: 10 EMA (Left) and 20 EMA (Right)
        row1_col1, row1_col2 = st.columns(2)
        with row1_col1:
            st.plotly_chart(create_individual_plot(df_breadth, '10 EMA', colors['10 EMA']), use_container_width=True)
        with row1_col2:
            st.plotly_chart(create_individual_plot(df_breadth, '20 EMA', colors['20 EMA']), use_container_width=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # ROW 2: 50 EMA (Left) and 200 EMA (Right)
        row2_col1, row2_col2 = st.columns(2)
        with row2_col1:
            st.plotly_chart(create_individual_plot(df_breadth, '50 EMA', colors['50 EMA']), use_container_width=True)
        with row2_col2:
            st.plotly_chart(create_individual_plot(df_breadth, '200 EMA', colors['200 EMA']), use_container_width=True)

        st.markdown("---")
        
        # 🎯 Dynamic Metric Overview 
        latest_row = df_breadth.iloc[-1]
        st.markdown(f"#### 🎯 Current Breadth Status (As of Last Trade Date: {latest_row['Date']})")
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        m_col1.metric("Above 10 EMA", f"{latest_row['10 EMA']}%")
        m_col2.metric("Above 20 EMA", f"{latest_row['20 EMA']}%")
        m_col3.metric("Above 50 EMA", f"{latest_row['50 EMA']}%")
        m_col4.metric("Above 200 EMA", f"{latest_row['200 EMA']}%")

        # Raw Table Preview
        st.markdown("### 📋 Filtered Historical Data Table")
        st.dataframe(df_breadth[['Date', '10 EMA', '20 EMA', '50 EMA', '200 EMA']].tail(20).iloc[::-1], use_container_width=True)
    else:
        st.warning("Selected date range me koi trading data available nahi hai.")
else:
    st.error("Failed to fetch NSE data. Please try again.")
