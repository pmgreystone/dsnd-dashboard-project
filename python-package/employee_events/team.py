from .query_base import QueryBase


class Team(QueryBase):
    '''
    Subclass for querying team details from the database
    '''

    name = "team"

    def names(self):
        '''
        Return a list of tuples containing team names and ids
        '''
        query = f"""
            SELECT team_name, team_id FROM {self.name}
            ORDER BY team_id ASC
        """
        result = self.pandas_query(query)
        return list(result.itertuples(index=False, name=None))

    def username(self, teamid):
        '''
        Return a list of tuples containing the team name for the given id
        Note: uses separate query, in place of using names method
        '''
        query = f"""
            SELECT team_name, team_id
            FROM {self.name}
            WHERE team_id = {teamid}
        """
        result = self.pandas_query(query)
        result = list(result.itertuples(index=False, name=None))
        if len(result) > 0:
            return result[0]
        else:
            return None

    def get_employees(self, teamid):
        query = f"SELECT employee_id FROM employee WHERE team_id = {teamid}"
        return self.query(query)

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
        return self.pandas_query(query)
