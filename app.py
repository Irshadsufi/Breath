import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. Page Configuration & App Headers
st.set_page_config(page_title="Nifty MidSmall 100-Stock Breadth", layout="wide")
st.title("📈 Nifty MidSmallcap Permanent 100-Stock Breadth")
st.markdown("### Date-wise % of Top 100 Liquid Mid & Small-cap Leaders Trading Above EMAs")
st.markdown("---")

# Sidebar Filters
st.sidebar.header("🎯 Dashboard Controls & Filters")

# 🔄 Manual Force Refresh Button
if st.sidebar.button("🔄 Clear Cache & Refresh Data"):
    st.cache_data.clear()
    st.toast("Cache Cleared! Re-fetching Fresh 100-Stock NSE Data...", icon="🚀")

# 2. Index Market Selection Toggle
market_type = st.sidebar.selectbox("Select Index Market:", ["Nifty MidSmall Top 100 Permanent Weights", "Nifty 50"])

# 🚀 LOCKED 100 HEAVYWEIGHT CONSTITUENTS (Midcap 150 + Smallcap 250 Top Actionable Mix)
MIDSML_100_PERMANENT = [
    # --- Top Midcaps, Infrastructure & Power Leaders ---
    'RECLTD.NS', 'PFC.NS', 'BHEL.NS', 'OIL.NS', 'GICRE.NS', 'IDBI.NS', 'BANKMAHA.NS', 
    'NMDC.NS', 'NATIONALUM.NS', 'YESBANK.NS', 'HAVELLS.NS', 'KALYANKJIL.NS', 'MCX.NS', 
    'CROMPTON.NS', 'GLENMARK.NS', 'STARHEALTH.NS', 'CARTRADE.NS', 'ACE.NS', 'IIFL.NS', 
    'FORCEMOT.NS', 'CHOLAFIN.NS', 'KARURVYSYA.NS', 'ICICIPRULI.NS', 'JMFINANCE.NS', 'LICHSGFIN.NS',
    'SHYAMMETL.NS', 'BSOFT.NS', 'POONAWALLA.NS', 'JSWENERGY.NS', 'IRFC.NS', 'RVNL.NS', 'HUDCO.NS', 
    'SAIL.NS', 'UNIONBANK.NS', 'CENTRALBK.NS', 'IOB.NS', 'ZOMATO.NS', 'JIOFIN.NS', 'IRCTC.NS', 
    'POLYCAB.NS', 'TATAELXSI.NS', 'KPITTECH.NS', 'PERSISTENT.NS', 'COFORGE.NS', 'MPHASIS.NS', 
    'DIXON.NS', 'ASTRAL.NS', 'SUPREMEIND.NS', 'BALKRISIND.NS', 'MRF.NS', 'APOLLOTYRE.NS', 
    'JKTYRE.NS', 'CEAT.NS', 'EXIDEIND.NS', 'AMARAJABAT.NS', 'VOLTAS.NS', 'BLUESTARCO.NS', 
    'WHIRLPOOL.NS', 'PAGEIND.NS', 'BATAINDIA.NS', 'RELAXO.NS', 'METROBRAND.NS',
    # --- High Beta Performance Smallcaps & Volume Buzzers ---
    'TATAINVEST.NS', 'NBCC.NS', 'SUZLON.NS', 'NHPC.NS', 'SJVN.NS', 'IRCON.NS', 'TITAGARH.NS', 
    'TEXRAIL.NS', 'BEML.NS', 'MAZDOCK.NS', 'GRSE.NS', 'COCHINSHIP.NS', 'BDL.NS', 'BEL.NS', 
    'HAL.NS', 'DATAPATTERNS.NS', 'CENTURYPLY.NS', 'GREENPANEL.NS', 'JINDALSTEL.NS', 'VEDL.NS', 
    'NCLIND.NS', 'NCC.NS', 'HFCL.NS', 'ITI.NS', 'TEJASNET.NS', 'STERTOOLS.NS', 'RAILTEL.NS', 
    'RITES.NS', 'MANINDS.NS', 'WELCORP.NS', 'ISGEC.NS', 'ENGINERSIN.NS', 'KEC.NS', 'OBEROIRLTY.NS',
    'CROMPTON.NS', 'CASTROLIND.NS', 'CESC.NS', 'SWANENERGY.NS', 'PPLPHARMA.NS', 'ALOKINDS.NS'
]

NIFTY_50_PERMANENT = [
    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'BHARTIARTL.NS', 'ICICIBANK.NS', 
    'INFY.NS', 'SBI.NS', 'ITC.NS', 'AXISBANK.NS', 'LT.NS', 'HCLTECH.NS', 'MARUTI.NS'
]

TICKERS = MIDSML_100_PERMANENT if "MidSmall" in market_type else NIFTY_50_PERMANENT

# 3. Default Timeframe Filters (Restored to exact clean 1 Year)
max_end_date = datetime.today()
default_start = max_end_date - timedelta(days=365)

st.sidebar.subheader("📅 Select Custom Date Range")
start_filter = st.sidebar.date_input("Start Date", default_start)
end_filter = st.sidebar.date_input("End Date", max_end_date)

def calculate_ema(series, length):
    return series.ewm(span=length, adjust=False).mean()

# High Performance Processing Engine
@st.cache_data(ttl=600)
def get_upgraded_breadth_data(market_name):
    selected_tickers = MIDSML_100_PERMANENT if "MidSmall" in market_name else NIFTY_50_PERMANENT
    end_date = datetime.today()
    start_date = end_date - timedelta(days=700) # Background buffer to secure historical 200 EMA math
    
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
                
                df.dropna(subset=['Close', 'EMA_10', 'EMA_20', 'EMA_50', 'EMA_200'], inplace=True)
                
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
    
    # Mathematical filtration to cleanly remove network anomaly outliers
    min_required_stocks = max(15, int(grouped['Total_Active'].max() * 0.5))
    grouped = grouped[grouped['Total_Active'] >= min_required_stocks].copy()
    
    grouped['10 EMA'] = round((grouped['A10'] / grouped['Total_Active']) * 100, 2)
    grouped['20 EMA'] = round((grouped['A20'] / grouped['Total_Active']) * 100, 2)
    grouped['50 EMA'] = round((grouped['A50'] / grouped['Total_Active']) * 100, 2)
    grouped['200 EMA'] = round((grouped['A200'] / grouped['Total_Active']) * 100, 2)
    
    return grouped[['Date', '10 EMA', '20 EMA', '50 EMA', '200 EMA']]

with st.spinner(f"Downloading real data for 100 stocks securely... Takes around 20-30 seconds..."):
    df_breadth_raw = get_upgraded_breadth_data(market_type)

def create_individual_plot(df, column_name, color):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['Date'], y=df[column_name], mode='lines', name=column_name, line=dict(color=color, width=2)
    ))
    fig.update_layout(
        title=dict(text=f"<b>{column_name} Breadth (100 Stocks Sample)</b>", font=dict(size=14)),
        xaxis_title="Date", yaxis_title="% Stocks Above", yaxis=dict(range=[0, 100]),
        hovermode="x unified", template="plotly_white", margin=dict(l=20, r=20, t=40, b=20), height=310
    )
    return fig

if not df_breadth_raw.empty:
    df_breadth_raw['Date_Parsed'] = pd.to_datetime(df_breadth_raw['Date'])
    mask = (df_breadth_raw['Date_Parsed'].dt.date >= start_filter) & (df_breadth_raw['Date_Parsed'].dt.date <= end_filter)
    df_breadth = df_breadth_raw.loc[mask].copy()

    if not df_breadth.empty:
        colors = {'10 EMA': '#e74c3c', '20 EMA': '#e67e22', '50 EMA': '#f1c40f', '200 EMA': '#2ecc71'}
        st.markdown("### 📊 Market Breadth Matrix (100-Stock Absolute Data Scan)")
        
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
        st.write("")
        m_col3.metric("Above 50 EMA", f"{latest_row['50 EMA']}%")
        m_col4.metric("Above 200 EMA", f"{latest_row['200 EMA']}%")

        st.markdown("#### ⚡ Market Momentum Signal")
        breadth_50 = latest_row['50 EMA']
        if breadth_50 >= 80: st.error(f"🔴 **Extreme Overbought Zone ({breadth_50}%)** - New swings me strict stoploss use karein.")
        elif breadth_50 >= 60: st.success(f"🟢 **Strong Bullish Momentum ({breadth_50}%)** - Market aggressive mode me chal raha hai.")
        elif breadth_50 <= 20: st.info(f"🔵 **Extreme Oversold Zone ({breadth_50}%)** - Fear peak par hai, sharp bounce accumulation taiyar karein.")
        else: st.warning(f"🟡 **Neutral Consolidated Market ({breadth_50}%)** - Stock-specific entries par dhyan dein.")

        st.markdown("---")
        st.markdown("### 📋 Filtered Historical Data Table")
        final_table = df_breadth[['Date', '10 EMA', '20 EMA', '50 EMA', '200 EMA']].iloc[::-1]
        csv_data = final_table.to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Download Full Breadth Excel Data (CSV)", data=csv_data, file_name="NSE_100Stock_Breadth.csv", mime="text/csv")
        st.dataframe(final_table.head(20), use_container_width=True)
else:
    st.error("Failed to fetch NSE records.")
