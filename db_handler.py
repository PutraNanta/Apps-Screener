import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import pandas as pd

# Load environment variables
load_dotenv()

def get_engine():
    """
    Membangun engine koneksi SQLAlchemy ke PostgreSQL
    berdasarkan variabel environment.
    """
    db_user = os.getenv('DB_USER', 'postgres')
    db_pass = os.getenv('DB_PASSWORD', 'postgres')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'stock_screener')
    
    # URL Format: postgresql+psycopg2://user:password@host:port/dbname
    connection_url = f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(connection_url)
    return engine

def init_db():
    """
    Inisialisasi database jika diperlukan.
    (Karena kita akan pakai Pandas to_sql, tabel bisa dibuat otomatis)
    Namun ini bisa dimanfaatkan jika butuh skema eksplisit.
    """
    engine = get_engine()
    # Anda bisa meletakkan logika pembuatan tabel statis di sini jika tidak ingin pakai to_sql
    pass

def get_stock_data(ticker, start_date=None, end_date=None):
    """
    Konektor untuk mengambil data dari database yang sudah di pre-calculate.
    Menggunakan SELECT ringan.
    """
    engine = get_engine()
    query = f"SELECT * FROM stock_history WHERE ticker = '{ticker}'"
    
    if start_date:
        query += f" AND date >= '{start_date}'"
    if end_date:
        query += f" AND date <= '{end_date}'"
        
    query += " ORDER BY date ASC"
    
    try:
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()

def get_available_tickers():
    """
    Mendapatkan list ticker yang ada di database.
    """
    engine = get_engine()
    query = "SELECT DISTINCT ticker FROM stock_history ORDER BY ticker ASC"
    try:
        df = pd.read_sql(query, engine)
        return df['ticker'].tolist()
    except Exception as e:
        return []
