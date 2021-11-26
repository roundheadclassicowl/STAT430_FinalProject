import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import datetime

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
slider_masks = jurisdiction['Date'].unique()
states = sorted(jurisdiction['Location'].unique())

idx = jurisdiction['Date'] == '11/24/2021'

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
            marks={i: '{}'.format(slider_masks[i]) for i in range(len(slider_masks))},
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
        )
    ], style={'width': '20%', 'display': 'inline-block', 'padding-left':'25%'}),

    html.Div([
            dcc.Dropdown(
                id='graph2_county',
                options=[{'label': i, 'value': i} for i in sorted(county['Recip_County'].unique())],
                value='Select County'
            ),
    ], style={'width': '20%', 'float': 'right', 'display': 'inline-block', 'padding-right':'25%'})

])

@app.callback(
    Output('graph1', 'figure'),
    Input('graph1_radio', 'value'),
    Input('graph1_date', 'value'))
def update_figure(selected_criteria, selected_date):
    idx = jurisdiction['Date'] == slider_masks[selected_date]

    print(selected_criteria, slider_masks[selected_date])
    if selected_criteria == 'FV':
        fig = go.Figure(data=go.Choropleth(
            locations=jurisdiction.loc[idx, 'Location'],  # Spatial coordinates
            z=jurisdiction.loc[idx, 'Series_Complete_Pop_Pct'].astype(float),  # Data to be color-coded
            locationmode='USA-states',  # set of locations match entries in `locations`
            colorscale='Blues',
            colorbar_title="Vaccine %",
        ))
    else:
        fig = go.Figure(data=go.Choropleth(
            locations=jurisdiction.loc[idx, 'Location'],  # Spatial coordinates
            z=jurisdiction.loc[idx, 'Administered_Dose1_Pop_Pct'].astype(float),  # Data to be color-coded
            locationmode='USA-states',  # set of locations match entries in `locations`
            colorscale='Blues',
            colorbar_title="Vaccine %",
        ))

    fig.update_layout(
        # title_text = '2011 US Agriculture Exports by State',
        geo_scope='usa',  # limite map scope to USA
    )
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)

