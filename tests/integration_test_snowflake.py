import os
import unittest
import pandas as pd
from datetime import datetime
from snowflake.connector import connect
from snowflake.connector.pandas_tools import write_pandas

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class TestSnowflakeIntegration(unittest.TestCase):

    def setUp(self):
        self.user = os.getenv('SNOWFLAKE_USER')
        self.password = os.getenv('SNOWFLAKE_PASSWORD')
        self.account = os.getenv('SNOWFLAKE_ACCOUNT')
        self.role = os.getenv('SNOWFLAKE_ROLE')
        self.warehouse = os.getenv('SNOWFLAKE_WAREHOUSE')
        self.database = os.getenv('SNOWFLAKE_DATABASE')
        self.schema = 'RAW'
        
        self.test_table = f'CI_TEST_{datetime.now().strftime("%Y%m%d_%H%M%S")}'

        self.df_mock = pd.DataFrame({
            'sale_date': ['2018-04-23 00:00:00', '2019-08-02 00:00:00'],
            'sales_person': ['Linda White', 'David Miller'],
            'customer_name': ['Pamela Sullivan', 'John Doe'],
            'car_make': ['Ford', 'Toyota'],
            'car_model': ['Altima', 'Corolla'],
            'car_year': ['2018', '2019'],
            'sale_price': ['48314', '25000'],
            'comm_rate': ['0.1468097182384521', '0.1200000000000000'],
            'comm_earned': ['7092.96', '3000.00'],
            'source_file': ['car_sales_data_2018_4.csv', 'car_sales_data_2018_4.csv'],
            'loaded_at': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')] * 2  
        })
    
    def test_connection_and_write(self):
        
        print(f'--- Initiating Integration Test on table: {self.test_table} ---')
        conn = None
        try:
            conn = connect(
                user=self.user,
                password=self.password,
                account=self.account,
                role=self.role,
                warehouse=self.warehouse,
                database=self.database,
                schema=self.schema
            )
            print('Connection to Snowflake established successfully.')

            success, _, n_rows, _ = write_pandas(
                conn,
                self.df_mock,
                self.test_table,
                auto_create_table=True,
                overwrite=True
            )

            self.assertTrue(success, 'The function write_pandas returned failure.')
            self.assertEqual(n_rows, 2, f'Expected 2 rows to be inserted, got {n_rows}.')
            print(f'Successful writing of {n_rows} rows.')

            cursor = conn.cursor()
            cursor.execute(f'SELECT COUNT(*) FROM {self.schema}.{self.test_table}')
            result = cursor.fetchone()[0]
            self.assertEqual(result, 2, 'The count in Snowflake does not match the DataFrame.')
            print('Data verification in Snowflake successful.')

        except Exception as e:
            self.fail(f'Integration test failed with exception: {str(e)}')
        
        finally:
            if conn:
                print('--- Cleaning up test table ---')
                cursor.execute(f'DROP TABLE IF EXISTS {self.schema}.{self.test_table}')
                conn.close()

if __name__ == '__main__':
    unittest.main()
