import dash
from dash import dcc, html, Input, Output, State,callback_context,no_update
import plotly.graph_objs as go
import pandas as pd
import dash_player
import os
import flask

# Classe Controls para o menu de controle
class ControlsChekpoint(html.Div):
    def __init__(self):
        atividades = [
                    'SITTING',
                    'STANDING',
                    'WALKING_UPSTAIRS',
                    'WALKING_DOWNSTAIRS',
                    'WALKING_SPONTANEOUS',
                    'RUN',
                    'WALKING_FAST',
                    'ELEVATOR_UP',
                    'ELEVATOR_DOWN',
                    'WALKING_IN_DOOR',
                    'DISTRACTED_WALKING'
]
        #change_points_name=df_protocol['change_point_name'].unique()
        change_points_time= ['timestamp_server', 'timestamp_local']
        super().__init__([
            html.Div([
                html.Div([
                    html.Label('Left label:', style={'margin-right': '2px'}),
                    dcc.Dropdown(
                        id='left-label',
                        options=[{'label': atividade, 'value': atividade} for atividade in atividades],
                        clearable=False,
                    ),
                ], style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'top'}),
                html.Div([
                    html.Label('Change point name:', style={'margin-right': '2px'}),
                    dcc.Dropdown(
                        id='change-point-name',
                        options=[],
                        clearable=False,
                    ),
                ], style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'top'}),
                html.Div([
                    html.Label('Change point time:', style={'margin-right': '2px'}),
                    dcc.Dropdown(
                        id='change-point-time',
                        options=[{'label': col, 'value': col} for col in change_points_time],
                        clearable=False,
                    ),
                ], style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'top'}),
            ], style={'width': '70%', 'display': 'inline-block'}),
            html.Div([
                # DELETE button
                html.Button('DELETE', id='btn-delete', n_clicks=0,disabled=True),
                # SAVE button
                html.Button('ADD', id='btn-add', n_clicks=0,disabled=True),
                #html.Button('UPDATE', id='btn-update', n_clicks=0)
            ], style={'width': '30%', 'display': 'inline-block'}),
            html.Div(id='save-output'),
            html.Div(id='zoomplot-logs', style={'color': 'red'}),
            dcc.ConfirmDialog(
                id='confirm-save',
                message='Do you really want to save the data?',
            ),
        ], style={'width': '100%'})
