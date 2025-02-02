# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

sites = list(set(spacex_df['Launch Site']))
sites.append('All')

junkdata=pd.DataFrame({'animal':['cat', 'dog', 'human'], 'legs':[4, 4, 2]})
# sites = list(spacex_df.groupby('Launch Site')['Launch Site'])
# print(sites)


# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                             options=sites,
                                             value='All',
                                             placeholder='Choose a launch site'
                                            ),
                                html.Br(),
                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                dcc.Graph(id='success-pie-chart', figure={}), #figure=px.pie(junkdata, names='animal', values='legs')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',min=min_payload, max=max_payload, value=[min_payload, max_payload], step=1000, marks={0: '0', 100: '100'}),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'), #figure
    Input(component_id='site-dropdown',component_property='value'))
def update_piechart(site):
    # print(site)
    if site != 'All':
        spacex_filtered = spacex_df[spacex_df['Launch Site']==site]
        success_rate = spacex_filtered['class'].mean()
        data=pd.DataFrame({'Outcome': ['Success', 'Failure'], 'Success':[success_rate, 1-success_rate]})
        return(px.pie(data, values='Success', names = 'Outcome', title=f"Launch Success Rate for Site {site}"))
    else:
        success_df = spacex_df[['class','Launch Site']].groupby('Launch Site').sum().reset_index()
        # print(success_df)
        return px.pie(success_df, values='class', names = 'Launch Site', title="Total successful launches per site")

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'), #figure
    [Input(component_id='payload-slider',component_property='value'),
    Input(component_id='site-dropdown',component_property='value')])
def update_piechart(weight_range, site):
    print(site)
    if weight_range is None: weight_range=[min_payload, max_payload]
    # print("Weight range:", weight_range[0], weight_range[1], type(weight_range[0]))
    spacex_filtered = spacex_df[spacex_df['Payload Mass (kg)'].ge(weight_range[0])]
    spacex_filtered = spacex_filtered[spacex_filtered['Payload Mass (kg)'].le(weight_range[1])]
    if site != 'All': spacex_filtered = spacex_filtered[spacex_filtered['Launch Site']==site]
    return px.scatter(spacex_filtered, x='Payload Mass (kg)',y='class', color="Booster Version Category", title="Fail/Success at Different Masses")

# Run the app
if __name__ == '__main__':
    app.run_server()
