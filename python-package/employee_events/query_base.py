import pandas as pd
import sqlite3
from pathlib import Path


class QueryBase:
    '''
    Class for querying the employee_events database
    '''

    name = ""
    db_path = Path(__file__).parent / "employee_events.db"

    def names(self):
        return []

    def notes(self, empid):
        '''
        Return df of notes
        '''
        conn = sqlite3.connect(self.db_path)
        tbl_name = "notes"

        select_clause = None
        where_clause = None
        if isinstance(empid, list):
            select_clause = "SELECT employee_id, note_date, note"
            empidstr = ','.join(map(str, empid))
            where_clause = f"employee_id IN ({empidstr})"
        else:
            select_clause = "SELECT note_date, note"
            where_clause = f"employee_id = {empid}"
        order_clause = " ORDER BY employee_id,note_date" if isinstance(
            empid, list) else " ORDER BY note_date"
        query = f"""
            {select_clause}
            FROM {tbl_name}
            WHERE {where_clause}
            {order_clause}
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def event_counts(self, empid):
        '''
        Return df of events
        '''
        conn = sqlite3.connect(self.db_path)
        tbl_name = "employee_events"
        query = f"""
            SELECT event_date, positive_events, negative_events
            FROM {tbl_name}
            WHERE employee_id = {empid}
            GROUP BY event_date
            ORDER BY event_date
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
