import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. Page Configuration & App Headers
st.set_page_config(page_title="NSE Multi-Sector Breadth Terminal", layout="wide")
st.title("🏛️ NSE Multi-Sector Breadth Analytics Terminal")
st.markdown("### Dynamic Sector Rotation Tracker: Fully Automated Smooth Indicators")
st.markdown("---")

# Sidebar Controls
st.sidebar.header("🎯 Terminal Controls")

if st.sidebar.button("🔄 Clear Cache & Refresh Terminal"):
    st.cache_data.clear()
    st.toast("Cache Cleared! Fetching Fresh Multi-Sector NSE Data...", icon="🚀")

# LARGE SCALE SECTOR MAPPING
SECTOR_MAP = {
    "Nifty MidSmall Top Dynamic Mix": [
        'RECLTD.NS', 'PFC.NS', 'BHEL.NS', 'OIL.NS', 'GICRE.NS', 'IDBI.NS', 'BANKMAHA.NS', 
        'NMDC.NS', 'NATIONALUM.NS', 'YESBANK.NS', 'HAVELLS.NS', 'KALYANKJIL.NS', 'MCX.NS', 
        'CROMPTON.NS', 'GLENMARK.NS', 'STARHEALTH.NS', 'CARTRADE.NS', 'ACE.NS', 'IIFL.NS', 
        'FORCEMOT.NS', 'CHOLAFIN.NS', 'KARURVYSYA.NS', 'ICICIPRULI.NS', 'JMFINANCE.NS', 'LICHSGFIN.NS',
        'SHYAMMETL.NS', 'BSOFT.NS', 'POONAWALLA.NS', 'JSWENERGY.NS', 'IRFC.NS', 'RVNL.NS', 'HUDCO.NS', 
        'SAIL.NS', 'UNIONBANK.NS', 'CENTRALBK.NS', 'IOB.NS', 'ZOMATO.NS', 'JIOFIN.NS', 'IRCTC.NS', 
        'POLYCAB.NS', 'TATAELXSI.NS', 'KPITTECH.NS', 'PERSISTENT.NS', 'COFORGE.NS', 'MPHASIS.NS', 
        'DIXON.NS', 'ASTRAL.NS', 'SUPREMEIND.NS', 'BALKRISIND.NS', 'MRF.NS', 'APOLLOTYRE.NS', 
        'JKTYRE.NS', 'CEAT.NS', 'EXIDEIND.NS', 'AMARAJABAT.NS', 'VOLTAS.NS', 'BLUESTARCO.NS', 
        'WHIRLPOOL.NS', 'PAGEIND.NS', 'BATAINDIA.NS', 'RELAXO.NS', 'METROBRAND.NS', 'NBCC.NS', 
        'SUZLON.NS', 'NHPC.NS', 'SJVN.NS', 'IRCON.NS', 'TITAGARH.NS', 'TEXRAIL.NS', 'BEML.NS', 
        'MAZDOCK.NS', 'GRSE.NS', 'COCHINSHIP.NS', 'BDL.NS', 'BEL.NS', 'HAL.NS', 'DATAPATTERNS.NS', 
        'CENTURYPLY.NS', 'GREENPANEL.NS', 'JINDALSTEL.NS', 'VEDL.NS', 'NCLIND.NS', 'NCC.NS', 
        'HFCL.NS', 'ITI.NS', 'TEJASNET.NS', 'STERTOOLS.NS', 'RAILTEL.NS', 'RITES.NS', 'MANINDS.NS', 
        'WELCORP.NS', 'ISGEC.NS', 'ENGINERSIN.NS', 'KEC.NS', 'OBEROIRLTY.NS', 'CASTROLIND.NS', 
        'CESC.NS', 'SWANENERGY.NS', 'PPLPHARMA.NS', 'ALOKINDS.NS'
    ],
    "IT (Information Technology)": ['TCS.NS', 'INFY.NS', 'WIPRO.NS', 'HCLTECH.NS', 'TECHM.NS', 'PERSISTENT.NS', 'COFORGE.NS', 'KPITTECH.NS', 'TATAELXSI.NS', 'MPHASIS.NS', 'BSOFT.NS', 'LTIM.NS', 'LTTS.NS', 'CYIENT.NS', 'SONATSOFTW.NS', 'ZENSARTECH.NS'],
    "Auto & Ancillaries": ['TATAMOTORS.NS', 'MARUTI.NS', 'M&M.NS', 'HEROMOTOCO.NS', 'BAJAJ-AUTO.NS', 'EICHERMOT.NS', 'BALKRISIND.NS', 'MRF.NS', 'APOLLOTYRE.NS', 'JKTYRE.NS', 'CEAT.NS', 'EXIDEIND.NS', 'AMARAJABAT.NS', 'TIINDIA.NS', 'SONACOMS.NS', 'BHARATFORG.NS'],
    "Metal & Mining": ['TATASTEEL.NS', 'JSWSTEEL.NS', 'HINDALCO.NS', 'NATIONALUM.NS', 'SAIL.NS', 'NMDC.NS', 'VEDL.NS', 'JINDALSTEL.NS', 'SHYAMMETL.NS', 'APLAPOLLO.NS', 'HINDZINC.NS', 'WELCORP.NS'],
    "Healthcare & Pharma": ['SUNPHARMA.NS', 'CIPLA.NS', 'DRREDDY.NS', 'DIVISLAB.NS', 'APOLLOHOSP.NS', 'GLENMARK.NS', 'PPLPHARMA.NS', 'LUPIN.NS', 'AUROPHARMA.NS', 'BIOCON.NS', 'MAXHEALTH.NS', 'MANKIND.NS', 'TORNTPHARM.NS', 'ALKEM.NS', 'IPCALAB.NS'],
    "Realty (Real Estate)": ['DLF.NS', 'GODREJPROP.NS', 'OBEROIRLTY.NS', 'LODHA.NS', 'PRESTIGE.NS', 'SOBHA.NS', 'BRIGADE.NS', 'NBCC.NS', 'PHOENIXLTD.NS', 'MAHINDSL.NS', 'SUNTECK.NS', 'INDIBULLS.NS'],
    "Defence & Aerospace": ['HAL.NS', 'BEL.NS', 'BDL.NS', 'MAZDOCK.NS', 'GRSE.NS', 'COCHINSHIP.NS', 'DATAPATTERNS.NS', 'BEML.NS', 'MTARTECH.NS', 'SOLARINDS.NS', 'AVANTEL.NS', 'ZENTECH.NS'],
    "Tourism, Hotels & Aviation": ['INDIGO.NS', 'IHCL.NS', 'IRCTC.NS', 'EIHOTEL.NS', 'LEMONTREE.NS', 'SPICEJET.NS', 'THOMASCOOK.NS', 'VIPIND.NS', 'YATRA.NS'],
    "Chemicals & Fertilizers": ['TATACHEM.NS', 'SRF.NS', 'DEEPAKNTR.NS', 'UPL.NS', 'PIIND.NS', 'NAVINFLUOR.NS', 'FLUOROCHEM.NS', 'CHAMBLFERT.NS', 'GNFC.NS', 'ATUL.NS', 'AARTIIND.NS', 'COROMANDEL.NS'],
    "Oil & Gas / Energy": ['RELIANCE.NS', 'ONGC.NS', 'BPCL.NS', 'OIL.NS', 'GAIL.NS', 'IOC.NS', 'HPCL.NS', 'PETRONET.NS', 'IGL.NS', 'MGL.NS', 'NTPC.NS', 'POWERGRID.NS', 'ADANIGREEN.NS', 'TATAPOWER.NS'],
    "Capital Markets & Exchanges": ['MCX.NS', 'BSE.NS', 'CDSL.NS', 'CAMS.NS', 'IEX.NS', 'KFINTECH.NS', 'ANGELONE.NS', 'MOTILALOFS.NS', 'ANANDRATHI.NS', 'GEOJITFSL.NS'],
    "Finance & Banking (BFSI)": ['HDFCBANK.NS', 'ICICIBANK.NS', 'SBI.NS', 'AXISBANK.NS', 'KOTAKBANK.NS', 'INDUSINDBK.NS', 'RECLTD.NS', 'PFC.NS', 'CHOLAFIN.NS', 'LICHSGFIN.NS', 'IRFC.NS', 'POONAWALLA.NS', 'JMFINANCE.NS', 'UNIONBANK.NS', 'CENTRALBK.NS', 'IOB.NS', 'BANKMAHA.NS', 'CANBK.NS', 'IDFCFIRSTB.NS', 'PNB.NS'],
    "Consumer Durables & Retail": ['TITAN.NS', 'HAVELLS.NS', 'VOLTAS.NS', 'BLUESTARCO.NS', 'WHIRLPOOL.NS', 'CROMPTON.NS', 'DIXON.NS', 'ZOMATO.NS', 'PAGEIND.NS', 'BATAINDIA.NS', 'RELAXO.NS', 'METROBRAND.NS', 'ABFRL.NS', 'TRENT.NS', 'VBL.NS', 'DMART.NS'],
    "Nifty 50 Core": ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'BHARTIARTL.NS', 'ICICIBANK.NS', 'INFY.NS', 'SBI.NS', 'ITC.NS', 'AXISBANK.NS', 'LT.NS', 'HCLTECH.NS', 'MARUTI.NS', 'ULTRACEMCO.NS', 'SUNPHARMA.NS', 'JSWSTEEL.NS', 'NTPC.NS']
}

selected_sector = st.sidebar.selectbox("🏛️ Select Market Sector:", list(SECTOR_MAP.keys()))

max_end_date = datetime.today() + timedelta(days=1)
default_start = max_end_date - timedelta(days=365)

st.sidebar.subheader("📅 Select Custom Date Range")
start_filter = st.sidebar.date_input("Start Date", default_start)
end_filter = st.sidebar.date_input("End Date", max_end_date)

def calculate_ema(series, length):
    return series.ewm(span=length, adjust=False).mean()

@st.cache_data(ttl=600)
def get_upgraded_breadth_data(sector_name):
    selected_tickers = SECTOR_MAP[sector_name]
    end_date = datetime.today() + timedelta(days=1)
    start_date = end_date - timedelta(days=700) 
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
    
    min_required_stocks = max(3, int(grouped['Total_Active'].max() * 0.4))
    grouped = grouped[grouped['Total_Active'] >= min_required_stocks].copy()
    
    grouped['10 EMA'] = round((grouped['A10'] / grouped['Total_Active']) * 100, 2)
    grouped['20 EMA'] = round((grouped['A20'] / grouped['Total_Active']) * 100, 2)
    grouped['50 EMA'] = round((grouped['A50'] / grouped['Total_Active']) * 100, 2)
    grouped['200 EMA'] = round((grouped['A200'] / grouped['Total_Active']) * 100, 2)
    
    return grouped[['Date', '10 EMA', '20 EMA', '50 EMA', '200 EMA']]

# --- Main Terminal Architecture Implementation ---
with st.spinner(f"Downloading data safely for {selected_sector}..."):
    breadth_df = get_upgraded_breadth_data(selected_sector)

if not breadth_df.empty:
    # Convert 'Date' column to standard datetime types for reliable filtering
    breadth_df['Date'] = pd.to_datetime(breadth_df['Date'])
    
    # Filter based on custom user parameters
    start_dt = pd.to_datetime(start_filter)
    end_dt = pd.to_datetime(end_filter)
    filtered_df = breadth_df[(breadth_df['Date'] >= start_dt) & (breadth_df['Date'] <= end_dt)].copy()
    
    if not filtered_df.empty:
        # 2. Metric Dashboard (Latest Available Values)
        latest_row = filtered_df.iloc[-1]
        st.markdown(f"#### 📈 Current Market Breadth Profile (As of: {latest_row['Date'].strftime('%d-%b-%Y')})")
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric(label="⚡ Stocks > 10 EMA (Momentum)", value=f"{latest_row['10 EMA']}%")
        m2.metric(label="🔥 Stocks > 20 EMA (Short-Term)", value=f"{latest_row['20 EMA']}%")
        m3.metric(label="💎 Stocks > 50 EMA (Medium-Term)", value=f"{latest_row['50 EMA']}%")
        m4.metric(label="🛡️ Stocks > 200 EMA (Structural Trend)", value=f"{latest_row['200 EMA']}%")
        
        st.markdown("---")
        
        # 3. Dynamic Chart Building via Plotly
        st.markdown(f"#### 📊 Multi-Timeframe Breadth Oscillator: {selected_sector}")
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(x=filtered_df['Date'], y=filtered_df['10 EMA'], name='10 EMA Breadth', line=dict(color='#FF5733', width=1.5)))
        fig.add_trace(go.Scatter(x=filtered_df['Date'], y=filtered_df['20 EMA'], name='20 EMA Breadth', line=dict(color='#FFC300', width=1.5)))
        fig.add_trace(go.Scatter(x=filtered_df['Date'], y=filtered_df['50 EMA'], name='50 EMA Breadth', line=dict(color='#33FF57', width=2.0)))
