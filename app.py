import streamlit as st
import plotly.graph_objects as go
from db_handler import get_stock_data, get_available_tickers

# Konfigurasi Halaman Streamlit
st.set_page_config(page_title="Stock Screener App", layout="wide")

st.title("📈 Stock Screener Application")
st.markdown("""
Aplikasi ini mendemonstrasikan **Slicing** (Form & Chart), **Konektor**, dan **Arsitektur** optimal
dengan menggunakan **2 Data Source** (Yahoo Finance & Stooq) dan pre-calculated indicators di PostgreSQL.
""")

# ==========================================
# SLICING 1: FORM AWAL (Sidebar)
# ==========================================
st.sidebar.header("⚙️ Parameter Screener")

available_tickers = get_available_tickers()

if not available_tickers:
    st.sidebar.warning("⚠️ Database kosong. Silakan jalankan `data_fetcher.py` terlebih dahulu untuk melakukan seeding data.")
    st.stop()

selected_ticker = st.sidebar.selectbox("Pilih Saham (Ticker)", available_tickers)

date_range = st.sidebar.date_input("Pilih Rentang Waktu", [])

st.sidebar.markdown("**Indikator Teknikal:**")
show_ma  = st.sidebar.checkbox("Moving Average (MA5, MA20, MA50)", value=True)
show_bb  = st.sidebar.checkbox("Bollinger Bands (BB)", value=True)

# ==========================================
# KONEKTOR: Form -> Database -> Chart
# ==========================================
start_date = None
end_date   = None
if len(date_range) == 2:
    start_date = date_range[0].strftime("%Y-%m-%d")
    end_date   = date_range[1].strftime("%Y-%m-%d")
elif len(date_range) == 1:
    start_date = date_range[0].strftime("%Y-%m-%d")

with st.spinner(f"Mengambil data {selected_ticker} dari Database..."):
    df = get_stock_data(selected_ticker, start_date, end_date)

if df.empty:
    st.info(f"Tidak ada data untuk {selected_ticker} pada rentang tanggal tersebut.")
    st.stop()

# ==========================================
# Info Data Source (Arsitektur)
# ==========================================
col1, col2, col3 = st.columns(3)
source_label = df['source'].iloc[0].upper() if 'source' in df.columns else "N/A"
col1.metric("Ticker", selected_ticker)
col2.metric("Data Source", source_label)
col3.metric("Jumlah Data", f"{len(df)} hari")

st.markdown("---")

# ==========================================
# SLICING 2: CHART PERHITUNGAN
# ==========================================
st.subheader(f"📊 Grafik Harga & Indikator: {selected_ticker}")

fig = go.Figure()

# Harga Close
fig.add_trace(go.Scatter(
    x=df['date'], y=df['close'],
    mode='lines', name='Harga Close',
    line=dict(color='#2196F3', width=2)
))

# Moving Average
if show_ma:
    ma_config = [
        ('ma5',  'MA 5',  '#FF9800', 1),
        ('ma20', 'MA 20', '#4CAF50', 1.5),
        ('ma50', 'MA 50', '#F44336', 1.5),
    ]
    for col, name, color, width in ma_config:
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df['date'], y=df[col],
                mode='lines', name=name,
                line=dict(color=color, width=width)
            ))

# Bollinger Bands
if show_bb and 'bb_upper' in df.columns and 'bb_lower' in df.columns:
    fig.add_trace(go.Scatter(
        x=df['date'], y=df['bb_upper'],
        mode='lines', name='BB Upper',
        line=dict(color='rgba(156,39,176,0.5)', width=1, dash='dash')
    ))
    fig.add_trace(go.Scatter(
        x=df['date'], y=df['bb_lower'],
        mode='lines', name='BB Lower',
        line=dict(color='rgba(156,39,176,0.5)', width=1, dash='dash'),
        fill='tonexty', fillcolor='rgba(156,39,176,0.08)'
    ))

fig.update_layout(
    height=600,
    xaxis_title="Tanggal",
    yaxis_title="Harga (USD/IDR)",
    template="plotly_white",
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)

# ==========================================
# Tabel Pre-calculated Data
# ==========================================
with st.expander("📋 Lihat Data Tabel (Pre-calculated dari Database)"):
    cols_to_show = [c for c in ['date', 'close', 'ma5', 'ma20', 'ma50', 'bb_upper', 'bb_lower', 'source'] if c in df.columns]
    st.dataframe(df[cols_to_show].tail(50), use_container_width=True)

st.markdown("---")
st.caption("Data Source 1: Yahoo Finance | Data Source 2: Stooq.com | Database: PostgreSQL")
