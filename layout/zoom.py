import dash
from dash import dcc, html, Input, Output,State
import plotly.graph_objs as go
import pandas as pd
import re
import utils as ut




configs={}
configs['line_chekpoint_color']='green'
configs['line_chekpoint_select_color']='blue'
configs['line_timestamp_color']='orange'


class LoadZoom(html.Div):
    def __init__(self):
       
        super().__init__([html.Div([
    dcc.Graph(
        id='line-plot_zoom',        
        config={
            'editable': True,  # Permitir edição
            'edits': {'shapePosition': True }
        },
        style={'width': '100%', 'display': 'inline-block'},
        ),
        html.Div(id='output-container'),
        html.Div(id='selected-values') 
        ], style={'backgroundColor': '#fff4cc', 'padding': '2px'})])

    def  register_callbacks(self,app):
        @app.callback(
                Output('zoomplot-logs', 'children',allow_duplicate=True),
                Output('stored_data_checkpoint', 'data', allow_duplicate=True),
                Output('change-point-name', 'options', allow_duplicate=True),
                Input('btn-add', 'n_clicks'),                
                State('left-label', 'value'),
                State('change-point-time', 'value'),
                State('dropdown_sensor_ref', 'value'),
                State('stored_timestamp', 'data'),
                State('stored_data_checkpoint', 'data'),
                State('file_name-protocol', 'children'),
                prevent_initial_call=True,
            )
        def display_df_protocol(n_clicks,left_label, change_point_time,dropdown_sensor_ref,current_time,data_protocol,protocol_file_name):
            if n_clicks is None:
                return dash.no_update,dash.no_update,dash.no_update
            if left_label is None or  change_point_time is None:
                return "You need to select the parameters left_label and change_point_time. ",dash.no_update,dash.no_update
            if data_protocol is None:
                df_protocol =pd.DataFrame(columns=ut.get_columns_df_protocol())
            else:
                df_protocol = pd.DataFrame(data_protocol)
             
            change_point_name="change_point_X"
            timestamp=current_time['timestamp']
            new_row = pd.DataFrame({
                    'left_label': [left_label],
                    'change_point_name': [change_point_name],
                    'change_point_time': [change_point_time],
                    'sensor_ref': [dropdown_sensor_ref],
                    'timestamp': [timestamp]
                })
             
            if not df_protocol.empty:
                if not df_protocol[df_protocol['timestamp'] == timestamp].empty:
                        return (f"Timestamp {timestamp} já existe em df_protocol. A nova linha não será adicionada."),dash.no_update,dash.no_update
                
            df_protocol = pd.concat([df_protocol, new_row], ignore_index=True)

            df_protocol = df_protocol.sort_values(by='timestamp').reset_index(drop=True)
            df_protocol = df_protocol.reset_index(drop=True)
            df_protocol['change_point_name'] = [f'change_point_{i+1}' for i in range(len(df_protocol))]
            df_protocol.to_csv(protocol_file_name, index=False)

            unique_names = df_protocol['change_point_name'].unique()
                    # Construa a lista de opções para o dropdown
            options = [{'label': name, 'value': name} for name in unique_names]
            return  "save ok",df_protocol.to_dict('records'),options
                    
                    
                    
                    
                   
            return "Dados salvos ok",df_protocol.to_dict('records')
             
            #return dash.no_update,dash.no_update



        @app.callback(
            [Output('zoomplot-logs', 'children', allow_duplicate=True),
            Output('left-label', 'value', allow_duplicate=True),                
            Output('change-point-name', 'value', allow_duplicate=True),
            Output('change-point-time', 'value', allow_duplicate=True),
            Output('line-plot_zoom', 'figure', allow_duplicate=True),
            Output('stored_data_checkpoint', 'data',allow_duplicate=True),
           
            ]
            
            ,

            [Input('line-plot_zoom', 'relayoutData'),
             State('line-plot_zoom', 'figure'),
             State('stored_data_checkpoint', 'data'),
             State('file_name-protocol', 'children')
             
             ],prevent_initial_call=True
        )
        def update_relayout_zoom(relayout_data,figure,data_protocol,protocol_file_name):
            if relayout_data is None:
                return "dash.no_update", dash.no_update,dash.no_update, dash.no_update, dash.no_update, dash.no_update

            print("Relayout Data:", relayout_data)
            #df_protocol = pd.DataFrame(data_protocol)
            #df_protocol = pd.read_csv('1_1_Device 1.csv')

            for key, value in relayout_data.items():
                index = ut.extract_index_from_key(key)

                if index is not None and index > 0:  # Evita o shape com índice 0 (timestamp_id)
                    #matching_line = df_protocol.iloc[index - 1]
                    shape=figure['layout']['shapes'][index]
                    shape_name=figure['layout']['shapes'][index]['name']
                    for annotation in figure['layout']['annotations']:
                        if annotation['text'] == shape_name:
                            # Atualize a posição x da annotation
                            annotation['x'] = shape['x0']+1  # Supondo que x0 é a nova posição x do shape
                            annotation['font'] = dict(color=configs['line_chekpoint_select_color'])
                            break

                    figure['layout']['shapes'][index]['line']['color']="blue"
                    left_label, change_point_name, change_point_time, sensor_ref = shape_name.split('__')

                    df_protocol = pd.DataFrame(data_protocol)
                    filtered_df = df_protocol[
                                (df_protocol['left_label'] == left_label) &
                                (df_protocol['change_point_name'] == change_point_name) &
                                (df_protocol['change_point_time'] == change_point_time) &
                                (df_protocol['sensor_ref'] == sensor_ref)
        ]
                    index_to_update = filtered_df.index[0]
                    df_protocol.at[index_to_update, 'timestamp'] = shape['x0']

                    # Reorganizar 'change_point_name' após exclusão de linhas
                   
                
                
                
                    df_protocol = df_protocol.sort_values(by='timestamp').reset_index(drop=True)
                    df_protocol = df_protocol.reset_index(drop=True)
                    df_protocol['change_point_name'] = [f'change_point_{i+1}' for i in range(len(df_protocol))]
                    df_protocol.to_csv(protocol_file_name, index=False)



                    
                    #updated_figure = ut.update_line_color(matching_line, figu'line're.copy())
                    return f' update {str(shape_name)}',left_label,change_point_name, change_point_time,figure,df_protocol.to_dict('records')

            return dash.no_update,dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    


        @app.callback(
            [
            Output('zoomplot-logs', 'children', allow_duplicate=True),
            Output('stored_data_checkpoint', 'data',allow_duplicate=True),
            Output('left-label', 'value'),
            Output('change-point-name', 'value'),
            Output('change-point-time', 'value')],
            Input('btn-delete', 'n_clicks'),
            State('stored_data_checkpoint', 'data'),
            State('left-label', 'value'),
            State('change-point-name', 'value'),
            State('change-point-time', 'value'),
            State('file_name-protocol', 'children')
            ,prevent_initial_call=True
        )
        def delete_elements(n_clicks,data_protocol, left_label, change_point_name, change_point_time,protocol_file_name):

            if left_label is None or change_point_name is None or  change_point_time is None:
                return "You need to select the parameters left_label and change_point_time. ",dash.no_update, dash.no_update, dash.no_update, dash.no_update
            if data_protocol is None:
                df_protocol =pd.DataFrame(columns=ut.get_columns_df_protocol())
                return "Não tem dados ",dash.no_update, dash.no_update, dash.no_update, dash.no_update

            
            df_protocol = pd.DataFrame(data_protocol)
            
            if n_clicks > 0:
                df_protocol = df_protocol[
                    (df_protocol['left_label'] != left_label) |
                    (df_protocol['change_point_name'] != change_point_name) |
                    (df_protocol['change_point_time'] != change_point_time)
                ]
                
                # Reorganizar 'change_point_name' após exclusão de linhas
                df_protocol = df_protocol.reset_index(drop=True)
                df_protocol['change_point_name'] = [f'change_point_{i+1}' for i in range(len(df_protocol))]
                
                # Reescrever o arquivo CSV
                df_protocol.to_csv(protocol_file_name, index=False)
                
                
                return "dados apagados",df_protocol.to_dict('records'),None,  None,  None  # Limpar o dropdown 'change-point-time'
            
            return dash.no_update,dash.no_update, dash.no_update, dash.no_update, dash.no_update

            


        """     @app.callback(
    Output('line-plot_zoom', 'figure', allow_duplicate=True),
    Input('stored_data_select_range', 'data'),
    Input('stored_min_max_data', 'data'),

    
    State('stored_timestamp', 'data'),
    State('stored_data_checkpoint', 'data'),

    State('line-plot_zoom', 'figure'),prevent_initial_call=True,
)
        def update_line_plot2(stored_data_select_range,stored_min_max_data,current_time,stored_chek,fig):

            if fig is None:
                
                fig = {
                        'layout': {
                            'autosize': True,
                            'margin': {'l': 0, 'r': 0, 't': 0, 'b': 0},
                            'plot_bgcolor': 'white',
                            'paper_bgcolor': 'gray',
                            'title': '',
                            'showlegend': False,
                            'modebar': {
                                'orientation': 'v'
                            },
                            'xaxis': {
                                'showgrid': True,  # Mostra as linhas de grade no eixo x
                                'gridcolor': 'black',  # Cor das linhas de grade
                                'gridwidth': 1  # Largura das linhas de grade
                            },
                            'yaxis': {
                                'showgrid': True,  # Mostra as linhas de grade no eixo y
                                'gridcolor': 'black',  # Cor das linhas de grade
                                'gridwidth': 1  # Largura das linhas de grade
                            }
                        }
                    }
            
            fig = go.Figure(fig) 
            if(stored_data_select_range):
                
                    x_data_sensor = stored_data_select_range.get('x', [])
                    y_data_sensor = stored_data_select_range.get('y', [])
            else:
                    x_data_sensor=[0,100]
                    y_data_sensor=[0,10]



                   #            
                        
            if len(fig.data) > 0:
                            # Atualizar o trace 0 existente
                            fig.data[0].x = x_data_sensor
                            fig.data[0].y = y_data_sensor
                            df_protocol = pd.DataFrame(stored_chek)
                            shapes=ut.update__line_timestamp(current_time['timestamp'])
                            fig['layout']['shapes'] =shapes+ ut.update_shapes(df_protocol,min(fig.data[0].x), max(fig.data[0].x),0,15)

            else:
                        fig.add_trace(
                            go.Scatter(
                                x=x_data_sensor,
                                y=y_data_sensor,
                                mode='lines+markers'  # Define o modo como 'lines+markers'
                            )
                        )

                
                
            

            return fig






        
        # Callback para capturar mudanças na posição das linhas e atualizar os dropdowns
        @app.callback(
            [Output('zoomplot-logs', 'children', allow_duplicate=True),
                Output('left-label', 'value', allow_duplicate=True),
                
            Output('change-point-name', 'value', allow_duplicate=True),
            Output('change-point-time', 'value', allow_duplicate=True),
            Output('line-plot_zoom', 'figure', allow_duplicate=True)],

            [Input('line-plot_zoom', 'relayoutData'),
             State('line-plot_zoom', 'figure'),
             State('stored_data_checkpoint', 'data'),
             
             ],prevent_initial_call=True
        )
        def update_dropdowns(relayout_data,figure,data_protocol):
            if relayout_data is None:
                return "dash.no_update", dash.no_update,dash.no_update, dash.no_update, dash.no_update

            print("Relayout Data:", relayout_data)
            df_protocol = pd.DataFrame(data_protocol)

            for key, value in relayout_data.items():
                index = ut.extract_index_from_key(key)
                if index is not None and index > 0:  # Evita o shape com índice 0 (timestamp_id)
                    matching_line = df_protocol.iloc[index - 1]
                    figure
                    
                    updated_figure = ut.update_line_color(matching_line, figure.copy())
                    return (str(matching_line),matching_line['left_label'],
                            matching_line['change_point_name'],
                            matching_line['change_point_time'],figure.copy())

            return str(relayout_data),dash.no_update, dash.no_update, dash.no_update, dash.no_update










 """