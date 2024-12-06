from dash import  dcc, html, Input, Output, State
import pandas as pd
import os
import dash

class LoadProtocol(html.Div):
    def __init__(self):
        super().__init__([
            html.Div([
                html.Label('ID:', style={'margin-right': '2px'}),
                dcc.Dropdown(
                    id='id-dropdown',
                    options=[{'label': i, 'value': i} for i in range(1, 11)],
                    value=1,
                    clearable=False
                )
            ], style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'top'}),
            html.Div([
                html.Label('Protocol:', style={'margin-right': '2px'}),
                dcc.Dropdown(
                    id='protocol-dropdown',
                    options=[{'label': i, 'value': i} for i in range(1, 11)],
                    value=1,
                    clearable=False
                )
            ], style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'top'}),
            html.Div([
                html.Label('Device:', style={'margin-right': '2px'}),
                dcc.Dropdown(
                    id='device-dropdown',
                    options=[{'label': 'Device 1', 'value': 'Device 1'}, {'label': 'Device 2', 'value': 'Device 2'}],
                    value='Device 1',
                    clearable=False
                )
            ], style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'top'}),
            html.Button('Load Data', id='load-protocol-button', n_clicks=0, disabled=True,
                style={'background-color': 'green', 'color': 'white', 'margin': '0 10px', 'vertical-align': 'top'}),
            html.Div(id='log-protocol',  style={'color': 'red'}),
            html.Div(id='file_name-protocol',  style={'color': 'red'}),
            dcc.Store(id='stored_data_checkpoint'),  # Armazena o DataFrame carregado
        ], style={'width': '100%', 'display': 'inline-block'})




        
    

    def register_callbacks(self, app):
        @app.callback(
            Output('log-protocol', 'children'),
            Output('file_name-protocol', 'children'),
            Output('stored_data_checkpoint', 'data'),
            Output('btn-delete', 'disabled'),
            Output('btn-add', 'disabled'),
            [Input('load-protocol-button', 'n_clicks')],
            [State('id-dropdown', 'value'), State('protocol-dropdown', 'value'), State('device-dropdown', 'value')],
            prevent_initial_call=True
        )
        def load_data(n_clicks, id_value, protocol_value, device_value):
            # Check if any dropdown value is None
            if None in [id_value, protocol_value, device_value]:                
                return "Please select valid values for ID, Protocol, and Device.", dash.no_update, dash.no_update,True,True

            # Construct the filename
            filename = f'{id_value}_{protocol_value}_{device_value}.csv'

            # Check if the file exists
            if not os.path.exists(filename):
                # Create an empty DataFrame with the required columns
                df = pd.DataFrame(columns=["timestamp", "left_label", "change_point_name", "change_point_time", "sensor_ref"])
                # Save the DataFrame to a CSV file
                df.to_csv(filename, index=False)
                # Return a message indicating that the file was created
                return f"File created: {filename}", filename,df.to_dict('records'),False,False
            else:
                try:
                    df = pd.read_csv(filename)
                    # Ensure the DataFrame contains the expected columns
                    expected_columns = ["timestamp", "left_label", "change_point_name", "change_point_time", "sensor_ref"]
                    for column in expected_columns:
                        if column not in df.columns:
                            df[column] = pd.NA  # Add missing columns with NA values
                    
                    data = df.to_dict('records')  # Convert DataFrame to a JSON-serializable format
                    return "",filename, data,False,False
                except Exception as e:
                    print(f"Error reading file: {e}")
                    # Return a DataFrame with expected columns in case of an error
                    df = pd.DataFrame(columns=["timestamp", "left_label", "change_point_name", "change_point_time", "sensor_ref"])
                    data = df.to_dict('records')
                    filename = "Error loading file"
                    return "",filename, data,False,False


                
        
                        