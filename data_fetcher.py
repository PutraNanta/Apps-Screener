import yfinance as yf
import pandas as pd
from db_handler import get_engine

def calculate_indicators(df):
    """
    Melakukan Pre-Calculation untuk indikator teknikal (Slicing terkecil dari algoritma).
    Menghitung:
    - MA5, MA20, MA50
    - Bollinger Bands (BB_Upper, BB_Lower) dengan periode 20 dan std 2.
    """
    if df.empty:
        return df

    # Menghitung Moving Average
    df['ma5'] = df['Close'].rolling(window=5).mean()
    df['ma20'] = df['Close'].rolling(window=20).mean()
    df['ma50'] = df['Close'].rolling(window=50).mean()

    # Menghitung Bollinger Bands (Periode 20, 2 Standar Deviasi)
    std20 = df['Close'].rolling(window=20).std()
    df['bb_upper'] = df['ma20'] + (std20 * 2)
    df['bb_lower'] = df['ma20'] - (std20 * 2)

    return df

def fetch_and_store_data(ticker, start_date='2020-01-01', end_date='2024-01-01', source='yahoo'):
    """
    Fungsi arsitektural: Data Source -> Pre-calculate -> Database
    Menghindari perhitungan saat runtime agar DB tidak kolaps.
    """
    print(f"Fetching data for {ticker} from {source}...")
    
    df = pd.DataFrame()
    try:
        # Kita hanya menggunakan yfinance karena library pandas_datareader rusak di versi pandas terbaru
        df = yf.download(ticker, start=start_date, end=end_date)
            
    except Exception as e:
        print(f"Failed to fetch data for {ticker}: {e}")
        return

    if df.empty:
        print(f"No data found for {ticker}")
        return

    # Normalisasi nama kolom untuk konsistensi
    # yf download mungkin mereturn MultiIndex columns di versi baru, pastikan kita reset jika perlu
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    # Pastikan index adalah 'Date' dan bukan multi-index
    if df.index.name != 'Date':
        df.index.name = 'Date'

    # Pre-calculate indikator
    print(f"Calculating indicators for {ticker}...")
    df = calculate_indicators(df)
    
    # Reset index agar Date menjadi kolom biasa
    df = df.reset_index()
    
    # Normalisasi nama kolom menjadi lowercase untuk PostgreSQL
    df.columns = [str(c).lower() for c in df.columns]
    
    # Tambahkan kolom ticker untuk identitas saham
    df['ticker'] = ticker

    # Simpan ke PostgreSQL
    print(f"Saving {ticker} data to database...")
    engine = get_engine()
    try:
        # Menyimpan ke tabel stock_history (append atau replace tergntung kebutuhan)
        # Di sini kita gunakan 'append', jadi data ditambahkan. 
        # (Catatan: dalam app produksi, butuh upsert / hapus duplikat)
        # Kita akan menghapus data lama untuk ticker ini jika update full history
        with engine.connect() as conn:
            try:
                conn.execute(f"DELETE FROM stock_history WHERE ticker = '{ticker}'")
            except:
                pass # Tabel belum ada
                
        df.to_sql('stock_history', engine, if_exists='append', index=False)
        print(f"Successfully saved {len(df)} rows for {ticker}")
    except Exception as e:
        print(f"Error saving to database: {e}")

if __name__ == "__main__":
    # Seeder: Menjalankan pengambilan data awal
    tickers_to_seed = ['AAPL', 'MSFT', 'BBCA.JK']
    
    print("Memulai proses Seeding Data Saham...")
    for t in tickers_to_seed:
        fetch_and_store_data(t, start_date='2022-01-01', end_date='2024-05-01', source='yahoo')
    
    print("Selesai! Data siap digunakan oleh aplikasi (hanya butuh SELECT).")
