import pytest
from pathlib import Path
from importlib import resources
from sqlite3 import connect
import pandas as pd

from employee_events import QueryBase, QueryMixin, Employee, Team
from employee_events import query

# assuming we're running from root
project_root = Path(__file__).parent.parent

# setup functions


@pytest.fixture
def db_path_value():
    package_name = 'employee_events'
    resource_name = 'employee_events.db'
    db_path = None
    with resources.path(package_name, resource_name) as path:
        db_path = path

    return db_path


@pytest.fixture
def db_conn(db_path_value):
    return connect(db_path_value)


@pytest.fixture
def table_names(db_conn):
    name_tuples = db_conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    return [x[0] for x in name_tuples]


@pytest.fixture
def employee(db_path_value):
    return Employee()


@pytest.fixture
def team(db_path_value):
    return Team()


@pytest.fixture
def query_base(db_path_value):
    return QueryBase()


@pytest.fixture
def query_mixin():
    return QueryMixin()


def test_db_exists(db_path_value):
    '''
    db path exists
    '''
    assert Path.exists(db_path_value)


def test_db_isfile(db_path_value):
    '''
    db path is file
    '''
    assert Path.is_file(db_path_value)


def test_employee_table_exists(table_names):
    '''
    string employee is in table_names
    '''
    assert 'employee' in table_names


def test_team_table_exists(table_names):
    '''
    string team is in table_names
    '''
    assert 'team' in table_names


def test_employee_events_table_exists(table_names):
    '''
    string employee_events is in table_names
    '''
    assert 'employee_events' in table_names


'''
simple names testing
'''


def test_employee_names(employee):
    result = employee.names()
    assert isinstance(result, list)
    assert all(isinstance(item, tuple) for item in result)


def test_team_names(team):
    result = team.names()
    assert isinstance(result, list)
    assert all(isinstance(item, tuple) for item in result)


def test_employee_username(employee):
    result = employee.username(1)
    assert isinstance(result, tuple)
    (full_name, employee_id) = result
    assert isinstance(full_name, str)
    assert isinstance(employee_id, int)


def test_team_username(team):
    result = team.username(1)
    assert isinstance(result, tuple)
    (team_name, team_id) = result
    assert isinstance(team_name, str)
    assert isinstance(team_id, int)


'''
query base
'''


def test_query_base_event_counts(query_base):
    result = query_base.event_counts(1)
    assert isinstance(result, pd.DataFrame)


def test_query_base_notes(query_base):
    result = query_base.notes(1)
    assert isinstance(result, pd.DataFrame)


'''
query mixin
'''


def test_query_mixin_pandas_query(query_mixin):
    sql_query = "SELECT 1"
    result = query_mixin.pandas_query(sql_query)
    assert isinstance(result, pd.DataFrame)


def test_query_mixin_query(query_mixin):
    sql_query = "SELECT 1"
    result = query_mixin.query(sql_query)
    assert isinstance(result, list)
    assert all(isinstance(item, tuple) for item in result)


'''
decorator testing
'''


def test_query_decorator():
    @query
    def sample_query():
        return "SELECT 1"

    result = sample_query()
    assert isinstance(result, list)
    assert all(isinstance(item, tuple) for item in result)


'''
model data testing
'''


def test_employee_model_data(employee):
    result = employee.model_data(1)
    assert isinstance(result, pd.DataFrame)


def test_team_model_data(team):
    result = team.model_data(1)
    assert isinstance(result, pd.DataFrame)
