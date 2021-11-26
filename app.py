import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import datetime
from urllib.request import urlopen
import json

with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties_map = json.load(response)

app = dash.Dash(__name__)
colors = {
    'background': '#FFFFFF',
    'text': '#000000'
}

# import datasets
county = pd.read_csv('data/COVID-19_Vaccinations_in_the_United_States_County.csv')
jurisdiction = pd.read_csv('data/COVID-19_Vaccinations_in_the_United_States_Jurisdiction.csv')
transmission = pd.read_csv('data/United_States_COVID-19_County_Level_of_Community_Transmission_as_Originally_Posted.csv')

# preprocess columns
g1_slider_masks = jurisdiction['Date'].unique()
g2_slider_masks = county['Date'].unique()
states = sorted(jurisdiction['Location'].unique())

idx = jurisdiction['Date'] == g1_slider_masks[0]

# figures and callbacks
fig = go.Figure(data=go.Choropleth(
    locations=jurisdiction.loc[idx, 'Location'], # Spatial coordinates
    z = jurisdiction.loc[idx, 'Series_Complete_Pop_Pct'].astype(float), # Data to be color-coded
    locationmode = 'USA-states', # set of locations match entries in `locations`
    colorscale = 'Blues',
    colorbar_title = "Vaccine %",
))

fig.update_layout(
    # title_text = '2011 US Agriculture Exports by State',
    geo_scope='usa', # limite map scope to USA
)

idx2 = (county['Recip_State'] == 'IL') & (county['Date'] == g2_slider_masks[0])

fig2 = px.choropleth(county[idx2], geojson=counties_map, locations='FIPS', color='Series_Complete_Pop_Pct',
                           color_continuous_scale="Viridis",
                           range_color=(0, 100),
                           labels={'unemp':'unemployment rate'}
                          )
fig2.update_geos(fitbounds="locations", visible=False)
fig2.update_layout(margin={"r":0,"t":0,"l":0,"b":0})


# web layout
app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='US COVID-19 DATA TRACKER',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }),

    html.Div(children='STAT430 Final Project, Fall 2021 -- Crescent Xiong.',
             style={
                 'textAlign': 'center',
                 'color': colors['text']
             }),

    html.Div(children=[
        html.Br(),
        html.Label(''),
        dcc.RadioItems(
            id='graph1_radio',
            options=[
                {'label': 'Fully Vaccinated', 'value': 'FV'},
                {'label': 'At least 1 dose', 'value': '1dose+'}
            ],
            value='FV'
        ),

        dcc.Graph(
            id='graph1',
            figure=fig
        ),

        html.Br(),
        html.Label('For Vaccine Up to Date'),
        dcc.Slider(
            id='graph1_date',
            min=0,
            max=7,
            marks={i: '{}'.format(g1_slider_masks[i]) for i in range(len(g1_slider_masks))},
            value=0,
        ),

    ], style={'textAlign': 'center', 'padding-left':'25%', 'padding-right':'25%'}),

    # separator

    html.Div(children=[
        dcc.Dropdown(
            id='graph2_state',
            options=[{'label': i, 'value': i} for i in states],
            value='Select State'
        ),
        dcc.RadioItems(
            id='graph2_radio',
            options=[
                {'label': 'Fully Vaccinated', 'value': 'FV'},
                {'label': 'At least 1 dose', 'value': '1dose+'}
            ],
            value='FV',
            labelStyle={'display': 'inline-block'}
        ),

    ], style={'width': '20%', 'display': 'inline-block', 'padding-left':'25%'}),

    html.Div([
        dcc.Dropdown(
            id='graph2_county',
            options=[{'label': i, 'value': i} for i in sorted(county['Recip_County'].unique())],
            value='Select County'
        ),
    ], style={'width': '20%', 'float': 'right', 'display': 'inline-block', 'padding-right': '25%'}),

    html.Div([
        dcc.Graph(
            id='graph2',
            figure=fig2
        ),

        dcc.Slider(
            id='graph2_date',
            min=0,
            max=4,
            marks={i: '{}'.format(g2_slider_masks[i]) for i in range(len(g2_slider_masks))},
            value=0,
        ),
    ], style={'width': '40%', 'display': 'inline-block', 'padding-left':'10%'}),

])

@app.callback(
    Output('graph1', 'figure'),
    Input('graph1_radio', 'value'),
    Input('graph1_date', 'value'))
def update_graph1(selected_criteria, selected_date):
    idx = jurisdiction['Date'] == g1_slider_masks[selected_date]

    print(selected_criteria, g1_slider_masks[selected_date])
    if selected_criteria == 'FV':
        color = 'Series_Complete_Pop_Pct'
    else:
        color = 'Administered_Dose1_Pop_Pct'

    fig = go.Figure(data=go.Choropleth(
        locations=jurisdiction.loc[idx, 'Location'],  # Spatial coordinates
        z=jurisdiction.loc[idx, color].astype(float),  # Data to be color-coded
        locationmode='USA-states',  # set of locations match entries in `locations`
        colorscale='Blues',
        colorbar_title="Vaccine %",
    ))

    fig.update_layout(
        # title_text = '2011 US Agriculture Exports by State',
        geo_scope='usa',  # limite map scope to USA
    )
    return fig

@app.callback(
    Output('graph2_county', 'options'),
    Input('graph2_state', 'value'))
def update_county_options(selected_state):
    county_idx = county['Recip_State'] == selected_state
    return [{'label': i, 'value': i} for i in sorted(county.loc[county_idx, 'Recip_County'].unique())]

@app.callback(
    Output('graph2', 'figure'),
    Input('graph2_state', 'value'),
    Input('graph2_radio', 'value'),
    Input('graph2_date', 'value'))
def update_graph2(selected_state, selected_criteria, selected_date):
    idx2 = (county['Recip_State'] == selected_state) & (county['Date'] == g2_slider_masks[selected_date])

    if selected_criteria == 'FV':
        color = 'Series_Complete_Pop_Pct'
    else:
        color = 'Administered_Dose1_Pop_Pct'

    fig2 = px.choropleth(county[idx2], geojson=counties_map, locations='FIPS', color=color,
                         color_continuous_scale="Viridis",
                         range_color=(0, 100),
                         title = 'County Level',
                         labels={color: 'Vaccine %', 'FIPS': 'Recip_County'}
                         )
    fig2.update_geos(fitbounds="locations", visible=False)
    fig2.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0},
                       legend=dict(
                           title='Vaccine %', orientation='h', y=1, yanchor="bottom", x=0.5, xanchor="center"
                       ))

    return fig2


if __name__ == '__main__':
    app.run_server(debug=True)

