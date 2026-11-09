import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. Page Configuration & Title
st.set_page_config(page_title="Nifty MidSmall 100 Breadth", layout="wide")
st.title("📈 Nifty MidSmallcap 100-Stock Breadth Dashboard")
st.markdown("### Date-wise % of Top 100 Liquid Mid & Small-cap Stocks Trading Above EMAs")
st.markdown("---")

# Sidebar Filters
st.sidebar.header("🎯 Dashboard Controls & Filters")

# 🔄 Force Refresh Button
if st.sidebar.button("🔄 Clear Cache & Refresh Data"):
    st.cache_data.clear()
    st.toast("Cache Cleared! Fetching Fresh 100-Stock NSE Data...", icon="🚀")

# 2. Index Selection
market_type = st.sidebar.selectbox("Select Index Market:", ["Nifty MidSmall Top 100 Heavyweights", "Nifty 50"])

# 🚀 UPGRADED: 100 Actionable Constituents (Top market-cap & liquid representation)
MIDSML_100_TICKERS = [
    # Top Midcaps & Power Houses
    'LICHSGFIN.NS', 'BHEL.NS', 'RECLTD.NS', 'PFC.NS', 'OIL.NS', 'GICRE.NS', 'IDBI.NS',
    'BANKMAHA.NS', 'NMDC.NS', 'NATIONALUM.NS', 'YESBANK.NS', 'HAVELLS.NS', 'KALYANKJIL.NS', 
    'MCX.NS', 'CROMPTON.NS', 'GLENMARK.NS', 'STARHEALTH.NS', 'CARTRADE.NS', 'ACE.NS', 
    'IIFL.NS', 'FORCEMOT.NS', 'CHOLAFIN.NS', 'KARURVYSYA.NS', 'ICICIPRULI.NS', 'JMFINANCE.NS',
    'SHYAMMETL.NS', 'BSOFT.NS', 'POONAWALLA.NS', 'JSWENERGY.NS', 'IRFC.NS', 'RVNL.NS',
    'HUDCO.NS', 'SAIL.NS', 'UNIONBANK.NS', 'CENTRALBK.NS', 'IOB.NS', 'ZOMATO.NS', 'JIOFIN.NS',
    'IRCTC.NS', 'POLYCAB.NS', 'TATAELXSI.NS', 'KPITTECH.NS', 'PERSISTENT.NS', 'COFORGE.NS',
    'MPHASIS.NS', 'DIXON.NS', 'ASTRAL.NS', 'SUPREMEIND.NS', 'BALKRISIND.NS', 'MRF.NS',
    'APOLLOTYRE.NS', 'JKTYRE.NS', 'CEAT.NS', 'EXIDEIND.NS', 'AMARAJABAT.NS', 'VOLTAS.NS',
    'BLUESTARCO.NS', 'WHIRLPOOL.NS', 'PAGEIND.NS', 'BATAINDIA.NS', 'RELAXO.NS', 'METROBRAND.NS',
    # Top Smallcap Performers & High Beta Traded
    'TATAINVEST.NS', 'HUDCO.NS', 'NBCC.NS', 'SUZLON.NS', 'NHPC.NS', 'SJVN.NS', 'IRCON.NS',
    'RVNL.NS', 'TITAGARH.NS', 'TEXRAIL.NS', 'BEML.NS', 'MAZDOCK.NS', 'GRSE.NS', 'COCHINSHIP.NS',
    'BDL.NS', 'BEL.NS', 'HAL.NS', 'DATAPATTERNS.NS', 'CENTURYPLY.NS', 'GREENPANEL.NS',
    'JINDALSTEL.NS', 'SAIL.NS', 'TATASTEEL.NS', 'HINDALCO.NS', 'VEDL.NS', 'NCLIND.NS',
    'NCC.NS', 'HFCL.NS', 'ITI.NS', 'TEJASNET.NS', 'STERTOOLS.NS', 'RAILTEL.NS', 'RITES.NS',
    'MANINDS.NS', 'WELCORP.NS', 'ISGEC.NS', 'ENGINERSIN.NS', 'KEC.NS', 'KALPATPOWR.NS'
]

NIFTY_50_TICKERS = [
    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'BHARTIARTL.NS', 'ICICIBANK.NS', 'INFY.NS', 'SBI.NS', 'ITC.NS'
]

TICKERS = MIDSML_100_TICKERS if "MidSmall" in market_type else NIFTY_50_TICKERS

# 3. Date Range Configuration (Default view set to 3 Years)
max_end_date = datetime.today()
default_start = max_end_date - timedelta(days=1000)

st.sidebar.subheader("📅 Select Custom Date Range")
start_filter = st.sidebar.date_input("Start Date", default_start)
end_filter = st.sidebar.date_input("End Date", max_end_date)

def calculate_ema(series, length):
    return series.ewm(span=length, adjust=False).mean()

# Safe batch processing to prevent timeout on 100 stocks
@st.cache_data(ttl=600)
def get_upgraded_breadth_data(market_name):
    selected_tickers = MIDSML_100_TICKERS if "MidSmall" in market_name else NIFTY_50_TICKERS
    end_date = datetime.today()
    start_date = end_date - timedelta(days=1200) 
    
    flat_records = list()
    progress_bar = st.progress(0)
    
    # Download data altogether safely via tickers mapping loop
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

# Fetch Data Engine
with st.spinner(f"Downloading data for 100 constituents safely... Please wait around 20-30 seconds."):
    df_breadth_raw = get_upgraded_breadth_data(market_type)

def create_individual_plot(df, column_name, color):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['Date'], y=df[column_name],
        mode='lines', name=column_name,
        line=dict(color=color, width=2)
    ))
    fig.update_layout(
        title=dict(text=f"<b>{column_name} Breadth Overview (100 Stocks Sample)</b>", font=dict(size=14)),
        xaxis_title="Date", yaxis_title="% Stocks Above",
        yaxis=dict(range=[0, 100]), hovermode="x unified",
        template="plotly_white", margin=dict(l=20, r=20, t=40, b=20), height=310
    )
    return fig

if not df_breadth_raw.empty:
    df_breadth_raw['Date_Parsed'] = pd.to_datetime(df_breadth_raw['Date'])
    mask = (df_breadth_raw['Date_Parsed'].dt.date >= start_filter) & (df_breadth_raw['Date_Parsed'].dt.date <= end_filter)
    df_breadth = df_breadth_raw.loc[mask].copy()

    if not df_breadth.empty:
        colors = {'10 EMA': '#e74c3c', '20 EMA': '#e67e22', '50 EMA': '#f1c40f', '200 EMA': '#2ecc71'}
        
        st.markdown("### 📊 Market Breadth Matrix (Top 100 Active Stocks)")
        
        # Row allocation 2x2
        row1_col1, row1_col2 = st.columns(2)
        with row1_col1:
            st.plotly_chart(create_individual_plot(df_breadth, '10 EMA', colors['10 EMA']), use_container_width=True)
        with row1_col2:
            st.plotly_chart(create_individual_plot(df_breadth, '20 EMA', colors['20 EMA']), use_container_width=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        row2_col1, row2_col2 = st.columns(2)
        with row2_col1:
            st.plotly_chart(create_individual_plot(df_breadth, '50 EMA', colors['50 EMA']), use_container_width=True)
        with row2_col2:
            st.plotly_chart(create_individual_plot(df_breadth, '200 EMA', colors['200 EMA']), use_container_width=True)

        st.markdown("---")
        
        latest_row = df_breadth.iloc[-1]
        st.markdown(f"#### 🎯 Current Breadth Status (As of Last Trade Date: {latest_row['Date']})")
        
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        m_col1.metric("Above 10 EMA", f"{latest_row['10 EMA']}%")
        m_col2.metric("Above 20 EMA", f"{latest_row['20 EMA']}%")
        m_col3.metric("Above 50 EMA", f"{latest_row['50 EMA']}%")
        m_col4.metric("Above 200 EMA", f"{latest_row['200 EMA']}%")

        # Market Momentum Signal
        st.markdown("#### ⚡ Market Momentum Signal")
        breadth_50 = latest_row['50 EMA']
        if breadth_50 >= 80:
            st.error(f"🔴 **Extreme Overbought Zone ({breadth_50}%)** - Market top lines par trade ho raha hai, momentum cooling active ho sakti hai.")
        elif breadth_50 >= 60:
            st.success(f"🟢 **Strong Bullish Momentum ({breadth_50}%)** - Quality midcaps me long setup build karte rahein.")
        elif breadth_50 <= 20:
            st.info(f"🔵 **Extreme Oversold Zone ({breadth_50}%)** - Fear peak par hai, sharp bounce-back accumulation trades plan karein.")
        else:
            st.warning(f"🟡 **Neutral Consolidated Market ({breadth_50}%)** - Range bound trading strategy use karein.")

        st.markdown("---")
        
        # Download Action
        st.markdown("### 📋 Filtered Historical Data Table")
        final_table = df_breadth[['Date', '10 EMA', '20 EMA', '50 EMA', '200 EMA']].iloc[::-1]
        
        csv_data = final_table.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download 100-Stock Breadth Data (CSV/Excel)",
            data=csv_data,
            file_name=f"NSE_100Stock_Breadth_{market_type}.csv",
            mime="text/csv"
        )
        st.dataframe(final_table.head(20), use_container_width=True)
    else:
        st.warning("Selected date range me koi trading data available nahi hai.")
else:
    st.error("Failed to fetch NSE data. Please try again.")
