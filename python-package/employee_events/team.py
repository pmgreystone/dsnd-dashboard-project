from .query_base import QueryBase
import pandas as pd
import sqlite3
from .sql_execution import query


class Team(QueryBase):
    '''
    Subclass for querying team details from the database
    '''

    name = "team"

    def names(self):
        '''
        Return a list of tuples containing team names and ids
        '''
        conn = sqlite3.connect(self.db_path)
        query = f"""
            SELECT team_name, team_id FROM {self.name}
            ORDER BY team_id ASC
        """
        result = pd.read_sql_query(query, conn)
        conn.close()
        return list(result.itertuples(index=False, name=None))

    def username(self, teamid):
        '''
        Return a list of tuples containing the team name for the given id
        Note: uses separate query, in place of using names method
        '''
        conn = sqlite3.connect(self.db_path)
        query = f"""
            SELECT team_name, team_id
            FROM {self.name}
            WHERE team_id = {teamid}
        """
        result = pd.read_sql_query(query, conn)
        conn.close()
        result = list(result.itertuples(index=False, name=None))
        if len(result) > 0:
            return result[0]
        else:
            return None

    @query
    def get_employees(self, teamid):
        return f"SELECT employee_id FROM employee WHERE team_id = {teamid}"

    def notes(self, teamid):
        '''
        Get all employees in that team id, and corr. notes
        '''
        employees = [id for id, in self.get_employees(teamid)]
        return super().notes(employees)

    def model_data(self, teamid):
        '''
        Return a pandas dataframe with the positive and negative events for the given team id
        '''
        conn = sqlite3.connect(self.db_path)
        tbl_name = "employee_events"
        query = f"""
            SELECT positive_events, negative_events FROM (
                    SELECT employee_id
                         , SUM(positive_events) positive_events
                         , SUM(negative_events) negative_events
                    FROM {self.name}
                    JOIN {tbl_name}
                        USING({self.name}_id)
                    WHERE {self.name}.{self.name}_id = {teamid}
                    GROUP BY employee_id
                   )
                """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
