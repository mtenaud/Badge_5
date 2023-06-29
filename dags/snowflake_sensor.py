from airflow.sensors.base import BaseSensorOperator
from airflow.utils.decorators import apply_defaults
from snowflake.connector import ProgrammingError
from airflow.hooks.base_hook import BaseHook
from snowflake.connector import SnowflakeConnection

class SnowflakeStreamSensor(BaseSensorOperator):
    @apply_defaults
    def __init__(
        self,
        snowflake_connection,
        stream_name,
        timeout=60 * 60,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.snowflake_connection = snowflake_connection
        self.stream_name = stream_name
        self.timeout = timeout

    def poke(self, context):
        # Retrieve Snowflake connection details
        conn = BaseHook.get_connection(self.snowflake_connection)
        snowflake_conn_params = {
            'user': conn.login,
            'password': conn.password,
            'account': conn.extra_dejson.get('account', None),
            'warehouse': conn.extra_dejson.get('warehouse', None),
            'database': conn.extra_dejson.get('database', None),
            'region': conn.extra_dejson.get('region', None),
            'role': conn.extra_dejson.get('role', None),
            'schema': conn.schema
        }

        # Establish a connection to Snowflake
        snowflake_conn = SnowflakeConnection(**snowflake_conn_params)
        try:
            with snowflake_conn.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {self.stream_name}")
                return cursor.rowcount > 0
        except ProgrammingError:
            return False
        finally:
            snowflake_conn.close()

"""
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.hooks.base_hook import BaseHook
from snowflake.connector import SnowflakeConnection

class SnowflakeStreamSensor(BaseOperator):

    @apply_defaults
    def __init__(self, snowflake_connection, stream_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.snowflake_connection = snowflake_connection
        self.stream_name = stream_name
        
    def execute(self, context):
        # Retrieve Snowflake connection details
        conn = BaseHook.get_connection(self.snowflake_connection)
        snowflake_conn_params = {
            'user': conn.login,
            'password': conn.password,
            'account': conn.extra_dejson.get('account', None),
            'warehouse': conn.extra_dejson.get('warehouse', None),
            'database': conn.extra_dejson.get('database', None),
            'region': conn.extra_dejson.get('region', None),
            'role': conn.extra_dejson.get('role', None),
            'schema': conn.schema
        }

        # Establish a connection to Snowflake
        snowflake_conn = SnowflakeConnection(**snowflake_conn_params)

        # Create a cursor object from the connection
        cursor = snowflake_conn.cursor()

        try:
            # Query the stream to check for new data
            query = f"SELECT * FROM {self.stream_name} LIMIT 1;"
            cursor.execute(query)

            # Fetch the first row from the result set
            result = cursor.fetchone()

            # If the query returns no rows, there is no new data
            if not result:
                self.log.info("No new data found in Snowflake stream.")
                return False

            self.log.info("New data found in Snowflake stream.")
            return True

        finally:
            # Close the cursor and the connection
            cursor.close()
            snowflake_conn.close()"""