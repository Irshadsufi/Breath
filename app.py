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

# LARGE SCALE SECTOR MAPPING (180+ Tickers for high data density and absolute smoothness)
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

max_end_date = datetime.today()
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
    
    grouped['Raw_10'] = round((grouped['A10'] / grouped['Total_Active']) * 100, 2)
    grouped['Raw_20'] = round((grouped['A20'] / grouped['Total_Active']) * 100, 2)
    grouped['Raw_50'] = round((grouped['A50'] / grouped['Total_Active']) * 100, 2)
    grouped['Raw_200'] = round((grouped['A200'] / grouped['Total_Active']) * 100, 2)
    
    grouped['10 EMA'] = round(grouped['Raw_10'].ewm(span=3, adjust=False).mean(), 2)
    grouped['20 EMA'] = round(grouped['Raw_20'].ewm(span=3, adjust=False).mean(), 2)
    grouped['50 EMA'] = round(grouped['Raw_50'].ewm(span=4, adjust=False).mean(), 2)
    grouped['200 EMA'] = round(grouped['Raw_200'].ewm(span=5, adjust=False).mean(), 2)
    
    # 🚀 10 SMA Signal Line logic tracking
    grouped['10_SMA_for_10_EMA'] = round(grouped['10 EMA'].rolling(window=10).mean(), 2)
    grouped['10_SMA_for_20_EMA'] = round(grouped['20 EMA'].rolling(window=10).mean(), 2)
    grouped['10_SMA_for_50_EMA'] = round(grouped['50 EMA'].rolling(window=10).mean(), 2)
    grouped['10_SMA_for_200_EMA'] = round(grouped['200 EMA'].rolling(window=10).mean(), 2)
    
    return grouped

with st.spinner(f"Downloading data safely... Please wait."):
    df_breadth_raw = get_upgraded_breadth_data(selected_sector)

def create_individual_plot(df, column_name, sma_column_name, color):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['Date'], y=df[column_name], mode='lines', name=column_name, line=dict(color=color, width=2.5)
    ))
    fig.add_trace(go.Scatter(
        x=df['Date'], y=df[sma_column_name], mode='lines', name="10 SMA Line", line=dict(color='#2c3e50', width=1.5, dash='dot')
    ))
    fig.update_layout(
        title=dict(text=f"<b>{column_name} Sector Breadth ({selected_sector})</b>", font=dict(size=14)),
        xaxis_title="Date", yaxis_title="% Stocks Above", yaxis=dict(range=[-5, 105]),
        hovermode="x unified", template="plotly_white", margin=dict(l=20, r=20, t=40, b=20), height=310, showlegend=True
    )
    return fig

# 🚀 FLAT SEQUENTIAL FLOW: Removed if/else checks to completely destroy Indentation errors
df_breadth_raw['Date_Parsed'] = pd.to_datetime(df_breadth_raw['Date'])
mask = (df_breadth_raw['Date_Parsed'].dt.date >= start_filter) & (df_breadth_raw['Date_Parsed'].dt.date <= end_filter)
