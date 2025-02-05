import pandas as pd
from pathlib import Path
import numpy as np
import random
import pickle
import json
from sqlite3 import connect
from datetime import timedelta, date
from sklearn.linear_model import LogisticRegression
from scipy.stats import norm, expon, uniform, skewnorm


class BuildProject:

    def __init__(self):
        self.data_path = Path.cwd() / 'source_data'
        self.profiles = self._create_profiles()
        self.employees = self._initialize_employees()
        self.daterange = pd.date_range(
            date.today() - timedelta(days=365), date.today())
        self.data = self._generate_data()
        self.df = self._create_dataframe()

    def _create_profiles(self):
        def left_skew(a, loc, size=500):
            r = skewnorm.rvs(a=a, loc=loc, size=size)
            r = r - min(r)
            r = r / max(r)
            r = r * loc
            r = r.astype(int)
            return random.choice(r)

        return {
            'good': {  # employee
                'positive': lambda: norm.rvs(loc=norm.rvs(4), scale=1).astype(int),
                'negative': lambda: expon.rvs(loc=0, scale=np.random.choice([.5, 1])).astype(int),
                'chance': .5
            },
            'normal': {  # employee
                'positive': lambda: norm.rvs(loc=norm.rvs(3), scale=1).astype(int),
                'negative': lambda: norm.rvs(loc=2, scale=np.random.choice([.5, 1, 2, 3])).astype(int),
                'chance': .15
            },
            'poor': {
                'positive': lambda: expon.rvs(loc=0, scale=.5).astype(int),
                'negative': lambda: norm.rvs(loc=.5).astype(int),
                'chance': .1
            },
            'chaotic_good': {  # employee
                'positive': lambda: left_skew(-1000, 5).astype(int),
                'negative': lambda: np.random.choice([0, np.random.choice([50, 200])], p=[.98, .02]),
                'chance': .2
            },
            'chotic_bad': {  # r :)
                'positive': lambda: expon.rvs(loc=0, scale=5).astype(int),
                'negative': lambda: left_skew(-1000, 10).astype(int),
                'chance': .2
            }
        }

    def _initialize_employees(self):
        '''
        - randomly assign profile type to an employee id
        - employee json maps to employee id
        - employee json however contains hardcoded notes
        - so the data is emulated only and is not mapped to
        - real world scenario, but profiles dist. for positive
        - events by profile, shows that good profiles have more
        - normalized dist. of positive events 📊
        '''
        employees = {}
        for employee_id in range(1, 26):
            employee_type = random.choice(list(self.profiles.keys()))
            event_distribution = self.profiles[employee_type]
            team_id = random.choice(range(1, 6))
            recruited = self._is_recruited(event_distribution['chance'])
            employees[employee_id] = {
                'employee_type': employee_type,
                'event_distribution': event_distribution,
                'team_id': team_id,
                'recruited': recruited
            }
        return employees

    def _is_recruited(self, chance):
        return np.random.choice([0, 1], p=[1-chance, chance])

    def _generate_data(self):
        data = []
        for day in self.daterange:
            if day.weekday() < 5:
                for employee, config in self.employees.items():
                    employee_type = config['employee_type']
                    positive = self.profiles[employee_type]['positive']()
                    negative = self.profiles[employee_type]['negative']()
                    data.append([
                        employee,
                        config['team_id'],
                        day.strftime('%Y-%m-%d'),
                        positive,
                        negative,
                        config['recruited'],
                    ])
        return data

    def _create_dataframe(self):
        df = pd.DataFrame(self.data, columns=[
            'employee_id', 'team_id', 'event_date',
            'positive_events', 'negative_events', 'recruited'
        ])

        employees_path = self.data_path / 'employees.json'
        managers_path = self.data_path / 'managers.json'
        shifts_path = self.data_path / 'shifts.json'
        teams_path = self.data_path / 'team_names.json'

        with employees_path.open('r') as file:
            employee = json.load(file)
        with managers_path.open('r') as file:
            managers = json.load(file)
        with shifts_path.open('r') as file:
            shift = json.load(file)
        with teams_path.open('r') as file:
            team_names = json.load(file)

        notes_list = []
        for idx, e in enumerate(employee, start=1):
            for note in e['notes']:
                notes_list.append([idx, e['name'], note])

        notes = pd.DataFrame(notes_list, columns=['employee_id', 'employee_name', 'note']).assign(
            event_date=np.random.choice(
                df.event_date, size=len(notes_list), replace=True)
        )

        df = df.merge(notes[['employee_id', 'event_date', 'note']], on=['employee_id', 'event_date'], how='left').merge(
            notes[['employee_id', 'employee_name']].drop_duplicates(), on=['employee_id'])

        df = df.assign(shift=df.team_id.apply(lambda x: shift[x-1]))

        team_map = {team: random.choice(managers)
                    for team in df.team_id.unique()}
        df['manager_name'] = df.team_id.map(team_map)
        df['team_name'] = df.team_id.apply(lambda x: team_names[x-1])

        return df

    def build_model(self, write=False):
        '''
        Returns model and dataframe with predictions
        '''
        events = self.df[['event_date', 'employee_id',
                          'team_id', 'positive_events', 'negative_events']]
        X = events.groupby('employee_id')[
            ['positive_events', 'negative_events']].sum()
        y = X.join(self.df.drop_duplicates('employee_id').set_index(
            'employee_id')[['recruited']]).recruited

        model = LogisticRegression(penalty=None)
        model.fit(X, y)
        X = X.assign(true=y, pred=model.predict_proba(X)[:, 1])

        model_path = Path.cwd().parent / 'assets' / 'model.pkl'
        if write:
            with model_path.open('wb') as file:
                pickle.dump(model, file)

        return (model, X)

    def export_db(self):
        employee = self.df.drop_duplicates('employee_id').assign(
            first_name=lambda x: x.employee_name.str.split().str[0],
            last_name=lambda x: x.employee_name.str.split().str[1],
        )[['employee_id', 'first_name', 'last_name', 'team_id']]

        events = self.df[['event_date', 'employee_id',
                          'team_id', 'positive_events', 'negative_events']]
        team = self.df.drop_duplicates(
            'team_id')[['team_id', 'team_name', 'shift', 'manager_name']]
        notes = self.df.dropna()[['employee_id', 'team_id', 'note', 'event_date']].rename(
            columns={'event_date': 'note_date'})

        db_path = Path.cwd().parent / 'python-package' / \
            'employee_events' / 'employee_events.db'
        connection = connect(db_path)

        employee.to_sql('employee', connection, if_exists='replace')
        team.to_sql('team', connection, if_exists='replace')
        notes.to_sql('notes', connection, if_exists='replace')
        events.to_sql('employee_events', connection, if_exists='replace')

        connection.close()


if __name__ == 'main':
    builder = BuildProject()
    model, df = builder.build_model(write=False)
    # builder.export_db()
