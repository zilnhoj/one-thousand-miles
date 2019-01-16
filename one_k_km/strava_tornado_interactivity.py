import pandas as pd
from bokeh.plotting import figure
from bokeh.layouts import layout, widgetbox
from bokeh.models import ColumnDataSource, HoverTool, BoxZoomTool, ResetTool, PanTool
from bokeh.models.widgets import Slider, Select, TextInput, Div
from bokeh.models import WheelZoomTool, SaveTool, LassoSelectTool
from bokeh.io import curdoc
from functools import lru_cache

from actual_vs_goal_cumulative import actual_goal_cumulative
from stacked_chart import stacked_bar_chart
from weekly_actual_goal import weekly_actual_goal
from static_summary import actual_weekly_vs_goal, summary_cumulative

@lru_cache()
def load_data():
    df = pd.read_csv('data/strava_data.csv', index_col=0)
    return df

@lru_cache()
def load_weekly():
    df = pd.read_csv('data/strava_weekly_data.csv', index_col=0)
    # df['week_number'] = df['week_number'].apply(str)
    return df

def select_weeks():
    """ Use the current selections to determine which filters to apply to the
    data. Return a dataframe of the selected data
    """
    df = load_data()

    # Determine what has been selected for each widgetd
    week_val = weeks_runs.value

    # Filter by week and weekly_actual_cumulative
    if week_val == "week 01":
        selected = df #[df.week == 'week 01']
    else:
        selected = df[(df.week == week_val)]

    desc.text = f"Week: {week_val}"
    return selected

def update():
    """ Get the selected data and update the data in the source
    """
    df_active = select_weeks()
    source.data = ColumnDataSource(data=df_active).data

def selection_change(attrname, old, new):
    """ Function will be called when the poly select (or other selection tool)
    is used. Determine which items are selected and show the details below
    the graph
    """
    selected = source.selected["1d"]["indices"]

    df_active = select_weeks()

    if selected:
        data = df_active.iloc[selected, :]
        temp = data.set_index("week").T.reindex(index=col_order)
        details.text = temp.style.render()
    else:
        details.text = "Selection Details"

run_data_df = load_data()
week_data_df = load_weekly()

all_weeks = list(load_data()['week'].unique())
all_week_number = list(load_weekly()['week_number'])
# print(all_week_number)
X_AXIS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']


desc = Div(text="Weekly runs", width=800)
weeks_runs = Select(title="Choose Week", options=all_weeks, value="Week 01")

source = ColumnDataSource(data=load_data())
weekly_source = ColumnDataSource(data=load_weekly())

summary_actual = actual_weekly_vs_goal(weekly_source, all_week_number)
cumulative_actual = summary_cumulative(weekly_source, all_week_number)
p = weekly_actual_goal(source, X_AXIS)
week_stacked_bar = stacked_bar_chart(source, X_AXIS)
weekly_actual_cumulative_fig = actual_goal_cumulative(source, X_AXIS)


controls = [weeks_runs]

for control in controls:
    control.on_change("value", lambda attr, old, new: update())

source.on_change("selected", selection_change)

inputs = widgetbox(*controls, sizing_mode="fixed")
l = layout([
            [summary_actual],
            [cumulative_actual],
            [desc],
            [weeks_runs],
            [weekly_actual_cumulative_fig],
            [p],
            [week_stacked_bar]], sizing_mode="scale_width")

update()
curdoc().add_root(l)
curdoc().title = "Yearly run analysis"

from urllib.parse import urlparse

from bokeh.embed import autoload_server
from flask import request


@main.route('/gaussian')
def gaussian():
    up = urlparse(request.url)
    scheme = up.scheme
    host = up.netloc
    port = up.port
    if port:
        host = host[:-(len(str(port)) + 1)]
    bokeh_server_url = '{scheme}://{host}:5100'.format(scheme=scheme, host=host)
    script = autoload_server(model=None, app_path='/gaussian', url=bokeh_server_url)
    return '<div>' + script + '</div>'

    # return render_template("chart.html")