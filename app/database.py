import os
from sqlalchemy import create_engine, Table, Column, Integer, String, Text, MetaData

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

DB_PATH = os.path.join(DATA_DIR, "table_store.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, echo=False)
metadata = MetaData()

table_store = Table(
    "table_store",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("store_index", String, unique=True, nullable=False),
    Column("encoded_data", Text, nullable=False),
)

metadata.create_all(engine)
