import dash
#import dash_core_components as dcc
#import dash_html_components as html
from dash import dcc
from dash import html


from dash.dependencies import Input, Output, State
import pandas as pd
import io
import base64




    
class ControlsLoadData(html.Div):
    def __init__(self):
        super().__init__([
            html.Div([
                html.Div([
                    html.Label('Sensor ref:', style={'margin-right': '2px'}),
                    dcc.Dropdown(
                        id='dropdown_sensor_ref',
                        options=[],
                        value='x',
                        clearable=False,
                    ),
                ], style={'width': '33%', 'display': 'inline-block', 'vertical-align': 'top'}),

                html.Div([
                    html.Label('Sensor:', style={'margin-right': '2px'}),
                    dcc.Dropdown(
                        id='dropdown_sensor_optional',
                        options=[],
                        clearable=False,
                    ),
                ], style={'width': '33%', 'display': 'inline-block', 'vertical-align': 'top'}),

                html.Div([
                    dcc.Upload(
                        id='upload-data',
                        children=html.Button('Upload data'),
                        multiple=False,
                         accept='.csv'
                    ),
                ], style={'width': '33%', 'display': 'inline-block', 'vertical-align': 'top', 'text-align': 'center'}),
            ], style={'width': '100%', 'display': 'flex', 'align-items': 'center'}),

            dcc.Store(id='stored_data_sensores'),dcc.Store(id='stored_min_max_data') ,

            html.Div(id='log_plot_brush', style={'width': '100%', 'margin-top': '10px'})
        ], style={'width': '100%'})


    def  register_callbacks(self,app):
        
        # Callback para processar o upload do CSV e armazenar os dados
        @app.callback(
            
            Output('stored_data_sensores', 'data',allow_duplicate=True),
            Output('log_plot_brush', 'children'),
            Output('load-protocol-button', 'disabled'),

            Input('upload-data', 'contents'),
            State('upload-data', 'filename'),prevent_initial_call=True,
        )
        def update_data(contents, filename):
            if contents is None:
                return dash.no_update, "No file uploaded"

            # Decodificar o conteúdo base64
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            df['sec'] = df['VideoTimelapse'] / 1000

            # Converta o DataFrame para um dicionário e armazene no dcc.Store
            data = df.to_dict('records')

            return data, f"File '{filename}' successfully uploaded and data stored.",True
        

    # Callback para atualizar os dropdowns com os nomes das colunas
        @app.callback(
            [Output('dropdown_sensor_ref', 'options'),
            Output('dropdown_sensor_optional', 'options')],
            Input('stored_data_sensores', 'data')
        )
        def update_dropdowns(data):
            if data is None:
                return dash.no_update, dash.no_update

            # Crie um DataFrame a partir dos dados armazenados
            df = pd.DataFrame(data)

            # Obtenha os nomes das colunas
            column_names = df.columns

            # Crie as opções para os dropdowns
            options = [{'label': col, 'value': col} for col in column_names]

            return options, options

