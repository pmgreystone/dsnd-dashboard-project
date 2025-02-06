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
        df = None
        with connect(db_path) as conn:
            df = pd.read_sql_query(sql_query, conn)
        return df

    def query(self, sql_query):
        '''
        Execute an SQL query and return the result as a list of tuples
        '''
        result = None
        with connect(db_path) as conn:
            cursor = conn.cursor()
            result = cursor.execute(sql_query).fetchall()
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
        result = None
        with connect(db_path) as conn:
            cursor = conn.cursor()
            result = cursor.execute(query_string).fetchall()
        return result

    return run_query
