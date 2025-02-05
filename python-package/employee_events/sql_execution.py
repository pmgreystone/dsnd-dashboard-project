import sqlite3
from sqlite3 import connect
from pathlib import Path
from functools import wraps
import pandas as pd


db_path = Path(__file__).parent / "employee_events.db"


class QueryMixin:

    def pandas_query(self, sql_query):
        '''
        Execute an SQL query and return the result as a pandas dataframe
        '''
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(sql_query, conn)
        conn.close()
        return df

    def query(self, sql_query):
        '''
        Execute an SQL query and return the result as a list of tuples
        '''
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(sql_query)
        result = cursor.fetchall()
        conn.close()
        return result

 # Leave this code unchanged


def query(func):
    '''
    Decorator that runs a standard sql execution
    and returns a list of tuples
    '''
    @wraps(func)
    def run_query(*args, **kwargs):
        query_string = func(*args, **kwargs)
        connection = connect(db_path)
        cursor = connection.cursor()
        result = cursor.execute(query_string).fetchall()
        connection.close()
        return result

    return run_query
