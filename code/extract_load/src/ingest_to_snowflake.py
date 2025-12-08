import os
import sys
import pandas as pd
from datetime import datetime
from snowflake.connector.pandas_tools import write_pandas
from snowflake.connector import connect

DATA_LAKE_PATH = "/opt/airflow/data_lake/car_sales_data"
DB = os.getenv('SNOWFLAKE_DATABASE')
SCHEMA = 'RAW'
TABLE = 'CAR_SALES'

def upload_to_snowflake(execution_date_str: str):
    
    try:
        date_obj = datetime.strptime(execution_date_str, '%Y-%m-%d')
    except ValueError:
        date_obj = datetime.strptime(execution_date_str.split('T')[0], '%Y-%m-%d')

    year = date_obj.year
    month = date_obj.month

    filename = f'car_sales_data_{year}_{month}.csv'
    filepath = os.path.join(DATA_LAKE_PATH, filename)

    if not os.path.exists(filepath):
        print(f'File {filename} does not exist. Assuming there were no sales this month.')
        sys.exit(0)
    
    try:
        df = pd.read_csv(filepath, dtype=str)
        print(f'Read {len(df)} records from {filename}.')
    except Exception as e:
        print(f'Error reading {filename}: {e}')
        sys.exit(1)
    
    df['_SOURCE_FILE'] = filename
    df['_LOADED_AT'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        conn = connect(
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PASSWORD'),
            account=os.getenv('SNOWFLAKE_ACCOUNT'),
            role=os.getenv('SNOWFLAKE_ROLE'),
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
            database=DB,
            schema=SCHEMA
        )

        success, _, nrows, _ = write_pandas(
            conn,
            df,
            TABLE,
            database=DB,
            schema=SCHEMA,
            auto_create_table=True,
            overwrite=False,
            chunk_size=100000,
            bulk_upload_chunks=True
        )

        if success:
            print(f'Successfully loaded {nrows} records into {DB}.{SCHEMA}.{TABLE}.')
        else:
            print('Failed to load data into Snowflake.')
            sys.exit(1)

    except Exception as e:
        print(f'Error loading data into Snowflake: {e}')
        sys.exit(1)
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        exec_date = sys.argv[1]
        upload_to_snowflake(exec_date)
    
    else:
        print('Error: You most provide the execution date as an argument.')
        sys.exit(1)
