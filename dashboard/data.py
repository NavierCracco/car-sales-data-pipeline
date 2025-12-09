import streamlit as st
import snowflake.connector
import polars as pl
from utils import get_secret

@st.cache_resource
def init_connection():
    """It establishes the connection to Snowflake and keeps it cached."""
    user = get_secret("SNOWFLAKE_USER")
    if not user:
        st.error("Credenciales no encontradas.")
        st.stop()

    return snowflake.connector.connect(
        account=get_secret("SNOWFLAKE_ACCOUNT"),
        user=user,
        password=get_secret("SNOWFLAKE_PASSWORD"),
        role=get_secret("SNOWFLAKE_ROLE"),
        warehouse=get_secret("SNOWFLAKE_WAREHOUSE"),
        database=get_secret("SNOWFLAKE_DATABASE"),
        schema=get_secret("SNOWFLAKE_SCHEMA")
    )

@st.cache_data
def load_data():
    """
    It loads the raw data from Snowflake and converts it to Polars.
    We bring in a large sample (1M rows) for in-memory filtering.
    """
    conn = init_connection()
    base_schema = get_secret("SNOWFLAKE_SCHEMA") or "PUBLIC"
    target_table = f"{base_schema}_MARTS.OBT_CAR_SALES"

    # --- PERFORMANCE OPTIMIZATION
    # Limit query to the recent 1M records to ensure dashboard responsiveness and prevent memory overload.
    # For full historical analysis (25M+ rows), direct Snowflake access or Power BI DirectQuery is recommended.
    query = f"SELECT * FROM {target_table} ORDER BY SALE_DATE DESC LIMIT 1000000"
    
    try:
        cur = conn.cursor()
        cur.execute(query)
        
        arrow_table = cur.fetch_arrow_all()
        df = pl.from_arrow(arrow_table)
        
        # Normalización
        new_cols = {col: col.lower() for col in df.columns}
        df = df.rename(new_cols)
        
        if 'sale_date' in df.columns:
            df = df.with_columns(pl.col("sale_date").cast(pl.Date))
            
        return df
    finally:
        conn.close()