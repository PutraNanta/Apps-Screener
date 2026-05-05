import yfinance as yf
import pandas as pd
import requests
from db_handler import get_engine
from sqlalchemy import text

# Flag untuk menandai apakah tabel sudah di-reset di sesi ini
_table_reset = False

# =========================================================
# DATA SOURCE 1: Yahoo Finance (Saham / Stock)
# =========================================================
def fetch_from_yahoo(ticker, start_date, end_date):
    """
    Data Source 1: Yahoo Finance via yfinance library.
    Mendukung saham US (AAPL, MSFT) dan Indonesia (BBCA.JK).
    """
    df = yf.download(ticker, start=start_date, end=end_date, progress=False)
    return df


# =========================================================
# DATA SOURCE 2: CoinGecko API (Kripto / Cryptocurrency)
# =========================================================
COINGECKO_ID_MAP = {
    'BTC': 'bitcoin',
    'ETH': 'ethereum',
    'BNB': 'binancecoin',
    'SOL': 'solana',
}

def fetch_from_coingecko(ticker, start_date, end_date):
    """
    Data Source 2: CoinGecko Public API (Gratis, tanpa API Key).
    Mengambil data OHLC harian untuk kripto (BTC, ETH, dll).
    Ticker format: 'BTC', 'ETH', 'SOL'
    """
    coin_id = COINGECKO_ID_MAP.get(ticker.upper())
    if not coin_id:
        print(f"  CoinGecko: Ticker '{ticker}' tidak dikenali. Gunakan: {list(COINGECKO_ID_MAP.keys())}")
        return pd.DataFrame()

    # Hitung jumlah hari dari start_date ke end_date
    from datetime import datetime
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt   = datetime.strptime(end_date,   '%Y-%m-%d')
    days = (end_dt - start_dt).days
    days = min(days, 365)  # CoinGecko OHLC max 365 hari untuk gratis

    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    headers = {'accept': 'application/json'}

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"  CoinGecko: HTTP {response.status_code} untuk {coin_id}")
            return pd.DataFrame()

        data = response.json()
        if not data:
            return pd.DataFrame()

        # Format respons: [[timestamp_ms, open, high, low, close], ...]
        df = pd.DataFrame(data, columns=['timestamp', 'Open', 'High', 'Low', 'Close'])
        df['Date'] = pd.to_datetime(df['timestamp'], unit='ms').dt.normalize()
        df = df.drop(columns=['timestamp'])
        df = df.set_index('Date')
        df.index.name = 'Date'

        # Ambil satu baris per hari (OHLC bisa ada duplikat per hari)
        df = df.groupby(df.index).last()
        df = df.sort_index()

        # Tambahkan Volume = 0 karena CoinGecko OHLC tidak include volume
        df['Volume'] = 0

        return df

    except Exception as e:
        print(f"  CoinGecko fetch error untuk {ticker}: {e}")
        return pd.DataFrame()


# =========================================================
# INDIKATOR TEKNIKAL (Pre-Calculation / Slicing Terkecil)
# =========================================================
def calculate_indicators(df):
    """
    Pre-Calculation indikator teknikal:
    - MA5, MA20, MA50 (Moving Average)
    - BB_Upper, BB_Lower (Bollinger Bands, periode 20, std 2)
    """
    if df.empty:
        return df

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    close_col = 'Close'
    df['ma5']  = df[close_col].rolling(window=5).mean()
    df['ma20'] = df[close_col].rolling(window=20).mean()
    df['ma50'] = df[close_col].rolling(window=50).mean()

    std20 = df[close_col].rolling(window=20).std()
    df['bb_upper'] = df['ma20'] + (std20 * 2)
    df['bb_lower'] = df['ma20'] - (std20 * 2)

    return df


# =========================================================
# PIPELINE UTAMA: Data Source -> Pre-calculate -> Database
# =========================================================
def fetch_and_store_data(ticker, start_date='2022-01-01', end_date='2024-05-01', source='yahoo'):
    """
    Arsitektur Utama:
    Data Source (Yahoo / CoinGecko) -> Pre-calculate (MA, BB) -> PostgreSQL
    Saat user buka UI, hanya perlu SELECT ringan dari database.
    """
    global _table_reset

    print(f"  [{source.upper()}] Fetching {ticker}...")

    df = pd.DataFrame()
    if source == 'yahoo':
        df = fetch_from_yahoo(ticker, start_date, end_date)
    elif source == 'coingecko':
        df = fetch_from_coingecko(ticker, start_date, end_date)
    else:
        print(f"  Data source '{source}' tidak dikenal.")
        return

    if df is None or df.empty:
        print(f"  Tidak ada data untuk {ticker} dari {source}.")
        return

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    print(f"  Menghitung indikator MA & BB untuk {ticker}...")
    df = calculate_indicators(df)

    df = df.reset_index()
    df.columns = [str(c).lower() for c in df.columns]
    df['ticker'] = ticker
    df['source'] = source

    engine = get_engine()
    try:
        if not _table_reset:
            # Reset tabel di awal agar schema selalu segar (termasuk kolom 'source')
            df.to_sql('stock_history', engine, if_exists='replace', index=False)
            _table_reset = True
        else:
            df.to_sql('stock_history', engine, if_exists='append', index=False)

        print(f"  Berhasil menyimpan {len(df)} baris untuk {ticker} [{source.upper()}]")
    except Exception as e:
        print(f"  Error menyimpan ke database: {e}")


# =========================================================
# SEEDER: Jalankan manual untuk mengisi data awal
# =========================================================
if __name__ == "__main__":
    print("=" * 55)
    print("Memulai Seeding Data Saham & Kripto (2 Data Sources)")
    print("=" * 55)

    # --- Data Source 1: Yahoo Finance (Saham) ---
    print("\n[DATA SOURCE 1] Yahoo Finance - Saham")
    yahoo_tickers = ['AAPL', 'BBCA.JK']
    for t in yahoo_tickers:
        fetch_and_store_data(t, start_date='2023-01-01', end_date='2024-05-01', source='yahoo')

    # --- Data Source 2: CoinGecko (Kripto) ---
    print("\n[DATA SOURCE 2] CoinGecko API - Kripto")
    crypto_tickers = ['BTC', 'ETH']
    for t in crypto_tickers:
        fetch_and_store_data(t, start_date='2023-01-01', end_date='2024-05-01', source='coingecko')

    print("\n" + "=" * 55)
    print("Selesai! Database siap dipakai (hanya perlu SELECT).")
    print("=" * 55)
