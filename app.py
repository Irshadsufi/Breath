import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. Page Configuration & Title
st.set_page_config(page_title="Nifty MidSmall 400 Breadth", layout="wide")
st.title("📈 Nifty MidSmallcap 400 Breadth Dashboard")
st.markdown("### Date-wise % of Mid & Small-cap Stocks Trading Above Selected EMAs")
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

# 3. EMA Selection Filter
st.sidebar.subheader("📐 Select EMAs to Display")
available_emas = ['10 EMA', '20 EMA', '50 EMA', '100 EMA', '200 EMA']
selected_emas = st.sidebar.multiselect("Choose EMA Lines:", available_emas, default=available_emas)

# 4. Date Filters
max_end_date = datetime.today()
default_start = max_end_date - timedelta(days=365)

st.sidebar.subheader("📅 Select Custom Date Range")
start_filter = st.sidebar.date_input("Start Date", default_start)
end_filter = st.sidebar.date_input("End Date", max_end_date)

# 5. Native EMA Calculation (No pandas-ta required)
def calculate_ema(series, length):
    return series.ewm(span=length, adjust=False).mean()

@st.cache_data(ttl=3600)
def get_upgraded_breadth_data(market_name):
    selected_tickers = MIDSML_400_TICKERS if "MidSmall" in market_name else NIFTY_50_TICKERS
    end_date = datetime.today()
    start_date = end_date - timedelta(days=550) 
    
    stock_dfs = {}
    progress_bar = st.progress(0)
    
    for i, ticker in enumerate(selected_tickers):
        try:
            df = yf.Ticker(ticker).history(start=start_date, end=end_date, auto_adjust=True)
            if not df.empty and len(df) >= 200:
                # Math based direct calculation
                df['EMA_10'] = calculate_ema(df['Close'], 10)
                df['EMA_20'] = calculate_ema(df['Close'], 20)
                df['EMA_50'] = calculate_ema(df['Close'], 50)
                df['EMA_100'] = calculate_ema(df['Close'], 100)
                df['EMA_200'] = calculate_ema(df['Close'], 200)
                stock_dfs[ticker] = df
        except Exception:
            continue
        progress_bar.progress((i + 1) / len(selected_tickers))
        
    progress_bar.empty()
    if not stock_dfs:
        return pd.DataFrame()

    first_key = list(stock_dfs.keys())
    trading_dates = list(stock_dfs[first_key].index)
    breadth_records = []
    
    for date in trading_dates:
        counts = {'Date': date.strftime('%Y-%m-%d'), '10 EMA': 0, '20 EMA': 0, '50 EMA': 0, '100 EMA': 0, '200 EMA': 0}
        total_active = 0
        
        for ticker, df in stock_dfs.items():
            if date in df.index:
                row = df.loc[date]
                close = float(row['Close'])
                
                if close > float(row['EMA_10']): counts['10 EMA'] += 1
                if close > float(row['EMA_20']): counts['20 EMA'] += 1
                if close > float(row['EMA_50']): counts['50 EMA'] += 1
                if close > float(row['EMA_100']): counts['100 EMA'] += 1
                if close > float(row['EMA_200']): counts['200 EMA'] += 1
                total_active += 1
                
        if total_active > 0:
            for key in ['10 EMA', '20 EMA', '50 EMA', '100 EMA', '200 EMA']:
                counts[key] = round((counts[key] / total_active) * 100, 2)
            breadth_records.append(counts)
            
    return pd.DataFrame(breadth_records)

# Run extraction
with st.spinner(f"Downloading data for {market_type} constituents..."):
    df_raw = get_upgraded_breadth_data(market_type)

if not df_raw.empty:
    df_raw['Date_Parsed'] = pd.to_datetime(df_raw['Date'])
    mask = (df_raw['Date_Parsed'].dt.date >= start_filter) & (df_raw['Date_Parsed'].dt.date <= end_filter)
    df_breadth = df_raw.loc[mask].copy()

    if not df_breadth.empty:
        if selected_emas:
            fig = go.Figure()
            colors = {'10 EMA': '#e74c3c', '20 EMA': '#e67e22', '50 EMA': '#f1c40f', '100 EMA': '#3498db', '200 EMA': '#2ecc71'}
            
            for ema in selected_emas:
                fig.add_trace(go.Scatter(
                    x=df_breadth['Date'], y=df_breadth[ema], 
                    mode='lines', name=ema, line=dict(color=colors[ema], width=2.5)
                ))
                
            fig.update_layout(
                title=f"<b>Market Breadth Dynamic Chart ({market_type})</b>",
                xaxis_title="Date", yaxis_title="% of Stocks Above EMA",
                yaxis=dict(range=[0, 100]), hovermode="x unified",
                template="plotly_white", height=600
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Kripya Sidebar se kam se kam ek EMA select karein chart dekhne ke liye.")
        
        latest_row = df_breadth.iloc[-1]
        st.markdown(f"#### 🎯 Current Breadth Status (As of Last Trade Date: {latest_row['Date']})")
        
        if selected_emas:
            cols = st.columns(len(selected_emas))
            for index, ema in enumerate(selected_emas):
                cols[index].metric(f"Above {ema}", f"{latest_row[ema]}%")

        st.markdown("### 📋 Filtered Historical Data Table")
        display_cols = ['Date'] + selected_emas
        st.dataframe(df_breadth[display_cols].tail(20).iloc[::-1], use_container_width=True)
    else:
        st.warning("Selected date range me koi trading data available nahi hai.")
else:
    st.error("Failed to fetch NSE data. Please try again.")

