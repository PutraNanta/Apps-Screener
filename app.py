import streamlit as st
import plotly.graph_objects as go
from db_handler import get_stock_data, get_available_tickers

# Konfigurasi Halaman Streamlit
st.set_page_config(page_title="Stock Screener App", layout="wide")

st.title("📈 Stock Screener Application")
st.markdown("""
Aplikasi ini menunjukkan **Slicing** (Form & Chart), **Konektor**, dan **Arsitektur** yang optimal. 
Data diambil dari database secara instan karena perhitungan berat (MA & Bollinger Bands) sudah dilakukan di *background* (Pre-calculated).
""")

# ==========================================
# 1. SLICING: FORM AWAL (Sidebar)
# ==========================================
st.sidebar.header("⚙️ Parameter Screener")

# Ambil daftar ticker yang tersedia di database
available_tickers = get_available_tickers()

if not available_tickers:
    st.sidebar.warning("⚠️ Database kosong. Silakan jalankan `data_fetcher.py` terlebih dahulu untuk melakukan seeding data.")
    selected_ticker = ""
else:
    selected_ticker = st.sidebar.selectbox("Pilih Saham (Ticker)", available_tickers)

# Pemilihan rentang waktu
date_range = st.sidebar.date_input(
    "Pilih Rentang Waktu",
    []
)

# Pemilihan Indikator yang ingin ditampilkan
st.sidebar.markdown("**Indikator Teknikal:**")
show_ma = st.sidebar.checkbox("Tampilkan Moving Average (MA)", value=True)
show_bb = st.sidebar.checkbox("Tampilkan Bollinger Bands (BB)", value=True)

# ==========================================
# 2. KONEKTOR & ARSITEKTUR
# ==========================================
if selected_ticker:
    start_date = None
    end_date = None
    
    if len(date_range) == 2:
        start_date = date_range[0].strftime("%Y-%m-%d")
        end_date = date_range[1].strftime("%Y-%m-%d")
    elif len(date_range) == 1:
        start_date = date_range[0].strftime("%Y-%m-%d")
        
    with st.spinner(f"Mengambil data {selected_ticker} dari Database..."):
        # Konektor memanggil get_stock_data (hanya operasi SELECT yang sangat ringan)
        df = get_stock_data(selected_ticker, start_date, end_date)
        
    if not df.empty:
        # ==========================================
        # 3. SLICING: CHART PERHITUNGAN
        # ==========================================
        st.subheader(f"Grafik Pergerakan Harga & Indikator: {selected_ticker}")
        
        # Membuat Chart Interaktif menggunakan Plotly
        fig = go.Figure()
        
        # Plot Harga Close
        fig.add_trace(go.Scatter(
            x=df['date'], y=df['close'],
            mode='lines', name='Close Price',
            line=dict(color='blue', width=2)
        ))
        
        # Plot Moving Average jika dicentang
        if show_ma:
            if 'ma5' in df.columns:
                fig.add_trace(go.Scatter(x=df['date'], y=df['ma5'], mode='lines', name='MA 5', line=dict(color='orange', width=1)))
            if 'ma20' in df.columns:
                fig.add_trace(go.Scatter(x=df['date'], y=df['ma20'], mode='lines', name='MA 20', line=dict(color='green', width=1.5)))
            if 'ma50' in df.columns:
                fig.add_trace(go.Scatter(x=df['date'], y=df['ma50'], mode='lines', name='MA 50', line=dict(color='red', width=1.5)))
                
        # Plot Bollinger Bands jika dicentang
        if show_bb:
            if 'bb_upper' in df.columns and 'bb_lower' in df.columns:
                # Upper Band
                fig.add_trace(go.Scatter(
                    x=df['date'], y=df['bb_upper'], 
                    mode='lines', name='BB Upper', 
                    line=dict(color='rgba(173, 216, 230, 0.5)', width=1, dash='dash')
                ))
                # Lower Band (dengan fill ke upper band)
                fig.add_trace(go.Scatter(
                    x=df['date'], y=df['bb_lower'], 
                    mode='lines', name='BB Lower', 
                    line=dict(color='rgba(173, 216, 230, 0.5)', width=1, dash='dash'),
                    fill='tonexty', fillcolor='rgba(173, 216, 230, 0.2)'
                ))

        fig.update_layout(
            height=600,
            xaxis_title="Tanggal",
            yaxis_title="Harga",
            template="plotly_white",
            hovermode="x unified"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Menampilkan Data Tabel (Opsional untuk pengecekan)
        with st.expander("Lihat Data Tabel (Pre-calculated)"):
            # Format tabel agar lebih mudah dibaca
            st.dataframe(df[['date', 'close', 'ma5', 'ma20', 'ma50', 'bb_upper', 'bb_lower']].tail(100))
            
    else:
        st.info(f"Tidak ada data untuk {selected_ticker} pada rentang tanggal tersebut.")
