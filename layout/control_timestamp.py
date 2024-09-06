
import dash
from dash import dcc, html, Input, Output, State,callback_context,no_update
import plotly.graph_objs as go
import pandas as pd
import dash_player
import os
import flask

class ControlsTimestamp(html.Div):
    def __init__(self):
        self.isPlaying = False
        super().__init__([
            html.Div([
            
            dcc.Slider(
                id='video-slider',
                min=0,
                #max=data['sec'].max(),
                step=0.1,
                #value=100,
                #marks={i: f'{i}s' for i in range(0, int(data['sec'].max()) + 1, 60)},
                included=False,
                vertical=False
            ),
            html.Div([
                html.Button('<', id='btn-back', n_clicks=0, style={'margin': '0 10px'}),
                html.Button('iniciar', id='btn-start', n_clicks=0, style={'margin': '0 10px'}),
                html.Button('>', id='btn-front', n_clicks=0, style={'margin': '0 10px'}),
            ], style={'margin-top': '10px', 'textAlign': 'center'}),
           
            
        ], style={'width': '100%', 'display': 'inline-block'})])


    
    
    def  register_callbacks(self,app):

        @app.callback(
            Output('stored_timestamp', 'data'),
            [Input('line-plot_zoom', 'relayoutData')],
            [State('stored_timestamp', 'data')],
            prevent_initial_call=True
        )
        def update_timestamp_from_relayout(relayout_data, current_timestamp):
            if relayout_data and 'shapes[0].x0' in relayout_data:
                # Obtém a nova posição x do shape no gráfico
                timestamp = relayout_data['shapes[0].x0']
                return {"timestamp": timestamp,'type':"plot_zoom"}
            return current_timestamp

    # Callback dedicado ao botão "Back"
        @app.callback(
            Output('stored_timestamp', 'data', allow_duplicate=True),
            Input('btn-back', 'n_clicks'),
            [State('stored_min_max_data', 'data'),
            State('stored_timestamp', 'data')],
            prevent_initial_call=True
        )
        def update_timestamp_back(n_clicks_back, min_max, current_time):
            if n_clicks_back:
                current_time = current_time['timestamp']
                timestamp = max(current_time - 50, min_max['x0'])
                return {"timestamp": timestamp,'type':"n_clicks_back"}

            return current_time

        # Callback dedicado ao botão "Front" (caso queira manter separado)
        @app.callback(
            Output('stored_timestamp', 'data', allow_duplicate=True),
            Input('btn-front', 'n_clicks'),
            [State('stored_min_max_data', 'data'),
            State('stored_timestamp', 'data')],
            prevent_initial_call=True
        )
        def update_timestamp_front(n_clicks_front, min_max, current_time):
            if n_clicks_front:
                current_time = current_time['timestamp']
                timestamp = min(current_time + 50, min_max['x1'])
                return {"timestamp": timestamp,'type':"n_clicks_front"}

            return current_time

        # Callback para atualização do timestamp do vídeo
        @app.callback(
            Output('stored_timestamp', 'data', allow_duplicate=True),
            Input('video-player', 'currentTime'),
            [State('stored_timestamp', 'data')],
            prevent_initial_call=True
        )
        def update_timestamp_video(timestamp_video, current_time):
            if timestamp_video:
                return {"timestamp": timestamp_video,'type':"video_player"}

            return current_time





    
    
    
        @app.callback(
                Output('line-plot_brush', 'figure', allow_duplicate=True),
                Input('stored_timestamp', 'data'),
                State('line-plot_brush', 'figure'),prevent_initial_call=True
            )
        def seek_back(current_time,figure_brush):
                if figure_brush is None:
                    return dash.no_update
                
                updated_figure_brush = figure_brush.copy()
                timestamp=current_time['timestamp']
                if current_time['type']=='n_clicks_front' or current_time['type']=='n_clicks_back':
                    updated_figure_brush['layout']['selections'][0]['x0']=timestamp-50
                    updated_figure_brush['layout']['selections'][0]['x1']=timestamp+50
                if 'shapes' in updated_figure_brush['layout']:
                    for shape in updated_figure_brush['layout'].get('shapes', []):
                        

                        if shape['name'] == 'timestamp_id':
                            shape_exists = True
                            shape['x0'] = timestamp
                            shape['x1'] = timestamp
                            return updated_figure_brush
                        



        @app.callback(
            Output('line-plot_zoom', 'figure', allow_duplicate=True),
            Input('stored_timestamp', 'data'),
            State('line-plot_zoom', 'figure'),
            prevent_initial_call=True
        )
        def seek_back(current_time, figure_brush):
            if figure_brush is None:
                return dash.no_update

            updated_figure_brush = figure_brush.copy()
            timestamp = current_time['timestamp']

            if current_time['type'] != 'plot_zoom':

                xaxis_range = updated_figure_brush['layout']['xaxis'].get('range', None)
                if xaxis_range is not None:
                    x_min, x_max = xaxis_range

                    if not (x_min <= timestamp <= x_max):
                        return dash.no_update

                if 'shapes' in updated_figure_brush['layout']:
                    for shape in updated_figure_brush['layout'].get('shapes', []):
                        if shape['name'] == 'timestamp_id':
                            shape_exists = True
                            shape['x0'] = timestamp
                            shape['x1'] = timestamp
                            return updated_figure_brush

            return dash.no_update
 
    
    
    
    
        
        
       