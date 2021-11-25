import dash
from dash import dcc
from dash import html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import datetime

app = dash.Dash(__name__)
colors = {
    'background': '#C0C0C0',
    'text': '#000000'
}

# import datasets
county = pd.read_csv('data/COVID-19_Vaccinations_in_the_United_States_County.csv')
jurisdiction = pd.read_csv('data/COVID-19_Vaccinations_in_the_United_States_Jurisdiction.csv')
transmission = pd.read_csv('data/United_States_COVID-19_County_Level_of_Community_Transmission_as_Originally_Posted.csv')

# preprocess columns
jurisdiction['Date'] = pd.to_datetime(jurisdiction['Date'])

idx = jurisdiction['Date'] == '11/24/2021'

# figures and callbacks
fig = go.Figure(data=go.Choropleth(
    locations=jurisdiction.loc[idx, 'Location'], # Spatial coordinates
    z = jurisdiction.loc[idx, 'Administered_Dose1_Pop_Pct'].astype(float), # Data to be color-coded
    locationmode = 'USA-states', # set of locations match entries in `locations`
    colorscale = 'Blues',
    colorbar_title = "Vaccine %",
))

fig.update_layout(
    # title_text = '2011 US Agriculture Exports by State',
    geo_scope='usa', # limite map scope to USA
)

# web layout
app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='US COVID-19 DATA TRACKER',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }),

    html.Div(children='Dash: A web application framework for your data.',
             style={
                 'textAlign': 'center',
                 'color': colors['text']
             }),

    html.Div(children=[
        html.Br(),
        html.Label(''),
        dcc.RadioItems(
            options=[
                {'label': 'Fully Vaccinated', 'value': 'FV'},
                {'label': 'At least 1 dose', 'value': '1dose+'}
            ],
            value='MTL'
        ),

        dcc.Graph(
            id='graph1',
            figure=fig
        ),

        # html.Br(),
        # html.Label('For Vaccine Up to Date'),
        # dcc.Slider(
        #     id='graph1_date',
        #     min=0,
        #     max=5,
        #     marks={date: 'Date {}'.format(date) for date in jurisdiction['Date']},
        #     value=0,
        # ),

    ], style={'textAlign': 'center'}),
])


if __name__ == '__main__':
    app.run_server(debug=True)

