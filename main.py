import numpy as np
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

ALL = 'All shapes'

df = pd.read_csv("Cleaned.csv", delimiter=';')

dash_app = dash.Dash(__name__)
app = dash_app.server

df['shape'] = df['shape'].replace(np.NaN, 'unknown')
df['shape'] = df['shape'].replace('changed', 'changing')

shapes = df['shape'].unique().tolist()
shapes.append(ALL)
shapes.sort()

options = [{'label': shape.capitalize(), 'value': shape} for shape in shapes]

height = 800

selected_value = ALL

dash_app.layout = html.Div([
    html.H1("Exploring UFO Sightings: Shapes Over Time", style={'text-align': 'center', 'margin-bottom': '20px'}),

    html.Div([
        html.Div([
            html.Label('Shapes:'),
            dcc.Dropdown(
                id='shapes_dropdown',
                options=options,
                value=selected_value,
                multi=False,
                clearable=False,
                ),
        ], style={'display': 'inline-block', 'width': '50%', 'margin': '20px'}),
        dcc.Graph(id='shapes_graph'),
    ], style={'margin-bottom': '20px', 'border': '1px solid grey'}),
    html.Footer(
        html.Small("By Martin Agnar Dahl - 2024")
        , style={"text-align": "center"})
])


@dash_app.callback(
    Output(component_id='shapes_dropdown', component_property='value'),
    [Input(component_id='shapes_graph', component_property='clickData')]
)
def update_dropdown_value(click_data):
    if click_data:
        shape_clicked = click_data['points'][0]['label']
        if type(shape_clicked) is int or shape_clicked.lower() not in shapes:
            raise dash.exceptions.PreventUpdate
        return shape_clicked.lower()
    else:
        return ALL


@dash_app.callback(
    Output(component_id='shapes_graph', component_property='figure'),
    [Input(component_id='shapes_dropdown', component_property='value')]
)
def update_graph(selected_shape):
    selected_shape = selected_shape.capitalize()
    if selected_shape == ALL:
        filtered_df = df
        filtered_df['shape'] = filtered_df['shape'].str.capitalize()
        shape_count = filtered_df.groupby('shape').size().reset_index(name='count')
        graph = px.bar(
            data_frame=shape_count,
            x='shape',
            y='count',
            height=height,
            hover_data=['shape'],
            color='shape',
            text='count',
        )

        hover_template = '<b>Shape:</b> %{label}<br><b>Count:</b> %{value}'

        graph.update_traces(
            textposition='outside',
            hovertemplate=hover_template)

        graph.update_layout(
            legend_title='Shapes',
            xaxis=dict(tickangle=90),
            xaxis_title='Shapes',
            yaxis_title='Total number of Sightings',
            uniformtext_minsize=12,
            uniformtext_mode='show',
            title={'text': 'Shapes of All Reported UFO Sightings', 'x': 0.5, 'font': {'size': 24}})
    else:
        filtered_df = df[df['shape'] == selected_shape]
        shape_per_year = filtered_df.groupby('year').size().reset_index(name='count')

        graph = px.bar(
            data_frame=shape_per_year,
            x='year',
            y='count',
            height=height,
            labels={'count': 'Count'},
            text='count'
        )
        hover_template = '<b>Year</b>: %{x}<br><b>Count</b>: %{y}'

        graph.update_traces(
            hovertemplate=hover_template,
            textposition='outside')

        graph.update_layout(
            xaxis=dict(dtick=2, tickangle=90),
            xaxis_title='Years',
            yaxis_title='Number of Sightings',
            title={'text': f'Shape "{selected_shape}" Across Years', 'x': 0.5, 'font': {'size': 24}})
    return graph


if __name__ == '__main__':
    dash_app.run_server(debug=True)
