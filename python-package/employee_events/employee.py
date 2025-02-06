from .query_base import QueryBase


class Employee(QueryBase):
    '''
    Subclass for querying employee details from the database
    '''

    name = "employee"

    def names(self):
        '''
        Return a list of tuples containing employee full names and ids
        '''
        query = f"""
            SELECT first_name || ' ' || last_name AS full_name, employee_id FROM {self.name}
            ORDER BY employee_id ASC
        """
        result = self.pandas_query(query)
        return list(result.itertuples(index=False, name=None))

    def username(self, empid):
        '''
        Return a list of tuples containing the full name of the employee with the given id
        '''
        all_names = self.names()
        result = [(full_name, employee_id)
                  for full_name, employee_id in all_names if employee_id == empid]
        if len(result) > 0:
            return result[0]
        else:
            return None

    def model_data(self, empid):
        '''
        Return a pandas dataframe with the summed positive and negative events for the given employee id
        '''
        tbl_name = "employee_events"
        query = f"""
            SELECT SUM(positive_events) positive_events
                , SUM(negative_events) negative_events
            FROM {self.name}
            JOIN {tbl_name}
                USING({self.name}_id)
            WHERE {self.name}.{self.name}_id = {empid}
        """
        return self.pandas_query(query)
