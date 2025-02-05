from .combined_components import CombinedComponent
from fasthtml import FastHTML
from fasthtml.common import H1, Div
from fasthtml.common import *
import matplotlib.pyplot as plt

# Import QueryBase, Employee, Team from employee_events
from employee_events import QueryBase, Employee, Team

# import the load_model function from the utils.py file
from .utils import load_model

"""
Below, we import the parent classes
you will use for subclassing
"""
from .base_components import (
    Dropdown,
    BaseComponent,
    Radio,
    MatplotlibViz,
    DataTable
)

from .combined_components import FormGroup, CombinedComponent


class ReportDropdown(Dropdown):

    def __init__(self, id="selector", name="entity-selection", label=""):
        self.employeeQuery = Employee()
        self.teamQuery = Team()
        super().__init__(id, name, label)

    def build_component(self, entity_id, name):  # model, name='assets/model'
        # Set the `label` attribute to the `name` attribute for the model

        self.label = name

        # Return the output from the parent class's build_component method
        names = self.employeeQuery.names(
        ) if self.label.name == 'employee' else self.teamQuery.names()
        return super().build_component(entity_id, names)

    def component_data(self, entity_id):  # removed model param
        # Using the model argument call the employee_events method
        # that returns the user-type's names and ids
        items = self.employeeQuery.names()
        data = None
        for fullname, empid in items:
            if empid == entity_id:
                data = fullname
                break
        return data


class Header(BaseComponent):

    def build_component(self, entity_id, model):
        # Using the model argument to return a fasthtml H1 object
        # containing the model's name attribute
        return H1(model.name)


class LineChart(MatplotlibViz):

    def visualization(self, asset_id, model):
        # Pass the `asset_id` argument to the model's `event_counts` method
        # to receive the x (Day) and y (event count)
        data = model.event_counts(asset_id)

        # Use the pandas .fillna method to fill nulls with 0
        data = data.fillna(0)

        # Use the pandas .set_index method to set the date column as the index
        data = data.set_index('event_date')

        # Sort the index
        data = data.sort_index()

        # Use the .cumsum method to change the data in the dataframe to cumulative counts
        data = data.cumsum()

        # Set the dataframe columns to the list ['Positive', 'Negative']
        data.columns = ['Positive', 'Negative']

        # Initialize a pandas subplot and assign the figure and axis to variables
        fig, ax = plt.subplots()

        # Call the .plot method for the cumulative counts dataframe
        data.plot(ax=ax)

        # Pass the axis variable to the `.set_axis_styling` method
        # Use keyword arguments to set the border color and font color to black
        self.set_axis_styling(ax, bordercolor='black', fontcolor='black')

        # Set title and labels for x and y axis
        ax.set_title('Cumulative Event Counts Over Time')
        ax.set_xlabel('Date')
        ax.set_ylabel('Cumulative Event Count')

        # Show the plot
        plt.show()

        return fig


class BarChart(MatplotlibViz):

    # Create a `predictor` class attribute
    # Assign the attribute to the output of the `load_model` utils function
    predictor = load_model()

    # Overwrite the parent class `visualization` method
    def visualization(self, asset_id, model):
        # Using the model and asset_id arguments
        # Pass the `asset_id` to the `.model_data` method to receive the data
        data = model.model_data(asset_id)

        # Using the predictor class attribute
        # Pass the data to the `predict_proba` method
        proba = self.predictor.predict_proba(data)

        # Index the second column of predict_proba output
        # The shape should be (<number of records>, 1)
        proba_column = proba[:, 1]

        # Create a `pred` variable set to the number we want to visualize
        if model.name == "team":
            # If the model's name attribute is "team", visualize the mean of the predict_proba output
            pred = proba_column.mean()
        else:
            # Otherwise set `pred` to the first value of the predict_proba output
            pred = proba_column[0]

        # Initialize a matplotlib subplot
        fig, ax = plt.subplots()

        # Run the following code unchanged
        ax.barh([''], [pred])
        ax.set_xlim(0, 1)
        ax.set_title('Predicted Recruitment Risk', fontsize=20)

        # Pass the axis variable to the `.set_axis_styling` method
        # Use keyword arguments to set the border color and font color to black
        self.set_axis_styling(ax, bordercolor='black', fontcolor='black')

        return fig


class Visualizations(CombinedComponent):

    # Set the `children` class attribute to a list containing an initialized instance of `LineChart` and `BarChart`
    children = [LineChart(), BarChart()]

    # Leave this line unchanged
    outer_div_type = Div(cls='grid')


class NotesTable(DataTable):

    # Overwrite the `component_data` method using the same parameters as the parent class
    def component_data(self, entity_id, model):
        # Using the model and entity_id arguments
        # Pass the entity_id to the model's .notes method. Return the output
        return model.notes(entity_id)


class DashboardFilters(FormGroup):

    id = "top-filters"
    action = "/update_data"
    method = "POST"

    children = [
        Radio(
            values=["Employee", "Team"],
            name='profile_type',
            hx_get='/update_dropdown',
            hx_target='#selector'
        ),
        ReportDropdown(
            id="selector",
            name="user-selection")
    ]


class Report(CombinedComponent):
    # Set the `children` class attribute to a list containing initialized instances
    # of the header, dashboard filters, data visualizations, and notes table
    children = [Header(), DashboardFilters(), Visualizations(), NotesTable()]


class MyFastHTMLApp:

    def build(self):
        app = FastHTML()
        report = Report()

        # Create a route for a get request
        # Set the route's path to the root

        @app.get('/')
        def get_root():
            # Call the initialized report, pass the integer 1 and an instance of the Employee class as arguments
            return report(1, Employee())

        # Create a route for a get request to receive a request for an employee ID
        # so `/employee/2` will return the page for the employee with an ID of `2`

        @app.get('/employee/{employee_id}')
        def get_employee(employee_id: str):
            # Call the initialized report, pass the ID and an instance of the Employee SQL class as arguments
            return report(employee_id, Employee())

        # Create a route for a get request to receive a request for a team ID
        # so `/team/2` will return the page for the team with an ID of `2`

        @app.get('/team/{team_id}')
        def get_team(team_id: str):
            # Call the initialized report, pass the ID and an instance of the Team SQL class as arguments
            return report(team_id, Team())

        # Keep the below code unchanged!

        @app.get('/update_dropdown{r}')
        def update_dropdown(r):
            dropdown = DashboardFilters.children[1]
            print('PARAM', r.query_params['profile_type'])
            if r.query_params['profile_type'] == 'Team':
                return dropdown(None, Team())
            elif r.query_params['profile_type'] == 'Employee':
                return dropdown(None, Employee())

        @app.post('/update_data')
        async def update_data(r):
            from fasthtml.common import RedirectResponse
            data = await r.form()
            profile_type = data._dict['profile_type']
            id = data._dict['user-selection']
            if profile_type == 'Employee':
                return RedirectResponse(f"/employee/{id}", status_code=303)
            elif profile_type == 'Team':
                return RedirectResponse(f"/team/{id}", status_code=303)

        # return the fasthtml app (with routing, build etc.) which also contains report view
        return app


app = MyFastHTMLApp().build()

# Start the application (if needed)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)
