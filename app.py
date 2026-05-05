import streamlit as st
import plotly.graph_objects as go
from db_handler import get_stock_data, get_available_tickers

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="MarketLens — Stock & Crypto Screener",
    page_icon="💹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CUSTOM CSS — Gradien, Modern Typography, Card Style
# =========================================================
st.markdown("""
<style>
/* === GOOGLE FONTS === */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* === GLOBAL === */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* === BACKGROUND === */
.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    min-height: 100vh;
}

/* === HERO HEADER === */
.hero-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border: 1px solid rgba(99, 102, 241, 0.3);
    border-radius: 20px;
    padding: 40px 48px;
    margin-bottom: 28px;
    box-shadow: 0 8px 32px rgba(99, 102, 241, 0.15);
}

.hero-badge {
    display: inline-block;
    background: linear-gradient(90deg, rgba(99,102,241,0.2), rgba(168,85,247,0.2));
    border: 1px solid rgba(99,102,241,0.4);
    color: #a5b4fc;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 6px 16px;
    border-radius: 50px;
    margin-bottom: 16px;
}

.hero-title {
    font-size: 42px;
    font-weight: 700;
    background: linear-gradient(135deg, #e0e7ff, #a5b4fc, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 8px 0 12px 0;
    line-height: 1.2;
}

.hero-subtitle {
    color: #94a3b8;
    font-size: 15px;
    font-weight: 400;
    line-height: 1.7;
    max-width: 680px;
}

/* === METRIC CARDS === */
.metric-grid {
    display: flex;
    gap: 16px;
    margin-bottom: 28px;
    flex-wrap: wrap;
}

.metric-card {
    flex: 1;
    min-width: 140px;
    background: linear-gradient(135deg, rgba(26,26,46,0.9), rgba(15,52,96,0.6));
    border: 1px solid rgba(99, 102, 241, 0.25);
    border-radius: 16px;
    padding: 20px 24px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    backdrop-filter: blur(10px);
}

.metric-label {
    color: #64748b;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 8px;
}

.metric-value {
    color: #e2e8f0;
    font-size: 22px;
    font-weight: 700;
}

.metric-badge {
    display: inline-block;
    margin-top: 6px;
    font-size: 11px;
    padding: 3px 10px;
    border-radius: 50px;
    font-weight: 500;
}

.badge-yahoo {
    background: rgba(234, 179, 8, 0.15);
    color: #fbbf24;
    border: 1px solid rgba(234,179,8,0.3);
}

.badge-coingecko {
    background: rgba(34, 197, 94, 0.15);
    color: #4ade80;
    border: 1px solid rgba(34,197,94,0.3);
}

/* === DIVIDER === */
.section-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(99,102,241,0.4), transparent);
    margin: 24px 0;
}

/* === CHART CONTAINER === */
.chart-container {
    background: linear-gradient(135deg, rgba(15,12,41,0.8), rgba(48,43,99,0.5));
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 20px;
    padding: 8px;
}

/* === SECTION TITLE === */
.section-title {
    font-size: 18px;
    font-weight: 600;
    color: #c7d2fe;
    margin-bottom: 4px;
}

.section-desc {
    font-size: 13px;
    color: #64748b;
    margin-bottom: 16px;
}

/* === SIDEBAR === */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f0c29 0%, #1a1a2e 100%);
    border-right: 1px solid rgba(99,102,241,0.2);
}

section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stDateInput label,
section[data-testid="stSidebar"] .stCheckbox label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #cbd5e1 !important;
}

/* === FOOTER === */
.footer-bar {
    margin-top: 32px;
    padding: 16px 0;
    text-align: center;
    color: #334155;
    font-size: 12px;
    border-top: 1px solid rgba(99,102,241,0.1);
}

/* === EXPANDER === */
.streamlit-expanderHeader {
    background: rgba(26,26,46,0.5) !important;
    color: #a5b4fc !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# HERO HEADER
# =========================================================
st.markdown("""
<div class="hero-header">
    <div class="hero-badge">💹 Market Intelligence Platform</div>
    <div class="hero-title">MarketLens Screener</div>
    <div class="hero-subtitle">
        Platform analisis teknikal real-time untuk saham dan aset kripto. 
        Visualisasikan Moving Average, Bollinger Bands, dan tren pasar dengan data 
        yang diambil dari <strong style="color:#a5b4fc">Yahoo Finance</strong> dan 
        <strong style="color:#4ade80">CoinGecko API</strong> — 
        diproses dan disimpan secara efisien di PostgreSQL.
    </div>
</div>
""", unsafe_allow_html=True)

# =========================================================
# SLICING 1: SIDEBAR FORM
# =========================================================
with st.sidebar:
    st.markdown("### ⚙️ Parameter Screener")
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    available_tickers = get_available_tickers()

    if not available_tickers:
        st.warning("⚠️ Database kosong. Jalankan `data_fetcher.py` terlebih dahulu.")
        st.stop()

    selected_ticker = st.selectbox("Pilih Aset", available_tickers)

    st.markdown("---")
    st.markdown("**📅 Rentang Waktu**")
    date_range = st.date_input("", [])

    st.markdown("---")
    st.markdown("**📊 Indikator Teknikal**")
    show_ma = st.checkbox("Moving Average (MA5 / MA20 / MA50)", value=True)
    show_bb = st.checkbox("Bollinger Bands (BB Upper / Lower)", value=True)

    st.markdown("---")
    st.markdown("""
    <div style='font-size:11px; color:#475569; line-height:1.8'>
    <strong style='color:#6366f1'>Data Source 1</strong><br>Yahoo Finance (Saham)<br><br>
    <strong style='color:#22c55e'>Data Source 2</strong><br>CoinGecko API (Kripto)
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# KONEKTOR: Ambil data dari Database
# =========================================================
start_date = None
end_date   = None
if len(date_range) == 2:
    start_date = date_range[0].strftime("%Y-%m-%d")
    end_date   = date_range[1].strftime("%Y-%m-%d")
elif len(date_range) == 1:
    start_date = date_range[0].strftime("%Y-%m-%d")

with st.spinner(f"Memuat data {selected_ticker}..."):
    df = get_stock_data(selected_ticker, start_date, end_date)

if df.empty:
    st.info(f"Tidak ada data untuk **{selected_ticker}** pada rentang waktu yang dipilih.")
    st.stop()

# =========================================================
# METRIC CARDS
# =========================================================
source_raw   = df['source'].iloc[0] if 'source' in df.columns else 'yahoo'
source_label = "Yahoo Finance" if source_raw == 'yahoo' else "CoinGecko API"
badge_class  = "badge-yahoo" if source_raw == 'yahoo' else "badge-coingecko"
latest_close = f"${df['close'].iloc[-1]:,.2f}"
data_points  = f"{len(df):,} hari"
latest_date  = str(df['date'].iloc[-1])[:10]

st.markdown(f"""
<div class="metric-grid">
    <div class="metric-card">
        <div class="metric-label">Aset</div>
        <div class="metric-value">{selected_ticker}</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Harga Terakhir</div>
        <div class="metric-value">{latest_close}</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Tanggal Data</div>
        <div class="metric-value" style="font-size:16px">{latest_date}</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Jumlah Data</div>
        <div class="metric-value">{data_points}</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Data Source</div>
        <div class="metric-value" style="font-size:15px">{source_label}</div>
        <span class="metric-badge {badge_class}">{source_raw.upper()}</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# =========================================================
# SLICING 2: CHART INTERAKTIF
# =========================================================
st.markdown(f"""
<div class="section-title">📈 Technical Analysis Chart — {selected_ticker}</div>
<div class="section-desc">Visualisasi harga penutupan dengan overlay indikator teknikal (MA & Bollinger Bands)</div>
""", unsafe_allow_html=True)

fig = go.Figure()

# Candlestick / Close Line
fig.add_trace(go.Scatter(
    x=df['date'], y=df['close'],
    mode='lines', name='Close Price',
    line=dict(color='#818cf8', width=2.5),
    fill='tozeroy',
    fillcolor='rgba(99,102,241,0.05)'
))

# Moving Average
if show_ma:
    ma_config = [
        ('ma5',  'MA 5',  '#f59e0b', 1.2),
        ('ma20', 'MA 20', '#34d399', 1.5),
        ('ma50', 'MA 50', '#f87171', 1.5),
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
        line=dict(color='rgba(168,85,247,0.6)', width=1, dash='dash')
    ))
    fig.add_trace(go.Scatter(
        x=df['date'], y=df['bb_lower'],
        mode='lines', name='BB Lower',
        line=dict(color='rgba(168,85,247,0.6)', width=1, dash='dash'),
        fill='tonexty',
        fillcolor='rgba(168,85,247,0.05)'
    ))

fig.update_layout(
    height=520,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(15,12,41,0.6)',
    font=dict(family='Inter', color='#94a3b8', size=12),
    xaxis=dict(
        title="Tanggal",
        gridcolor='rgba(99,102,241,0.08)',
        linecolor='rgba(99,102,241,0.2)',
        showgrid=True
    ),
    yaxis=dict(
        title="Harga (USD)",
        gridcolor='rgba(99,102,241,0.08)',
        linecolor='rgba(99,102,241,0.2)',
        showgrid=True
    ),
    hovermode="x unified",
    legend=dict(
        orientation="h",
        yanchor="bottom", y=1.02,
        xanchor="right", x=1,
        bgcolor='rgba(15,12,41,0.8)',
        bordercolor='rgba(99,102,241,0.3)',
        borderwidth=1
    ),
    margin=dict(l=0, r=0, t=40, b=0)
)

st.plotly_chart(fig, use_container_width=True)

# =========================================================
# DATA TABLE
# =========================================================
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

with st.expander("📋  Lihat Tabel Data Pre-Calculated (50 baris terakhir)"):
    cols = [c for c in ['date','close','ma5','ma20','ma50','bb_upper','bb_lower','source'] if c in df.columns]
    st.dataframe(
        df[cols].tail(50).style.format({
            'close': '{:.2f}', 'ma5': '{:.2f}', 'ma20': '{:.2f}',
            'ma50': '{:.2f}', 'bb_upper': '{:.2f}', 'bb_lower': '{:.2f}'
        }),
        use_container_width=True
    )

# =========================================================
# FOOTER
# =========================================================
st.markdown("""
<div class="footer-bar">
    MarketLens Screener &nbsp;·&nbsp; Data Source: Yahoo Finance & CoinGecko API &nbsp;·&nbsp; 
    Database: PostgreSQL &nbsp;·&nbsp; Built with Python & Streamlit
</div>
""", unsafe_allow_html=True)
