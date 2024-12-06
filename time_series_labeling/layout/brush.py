import pandas as pd
import dash
from dash import dcc, html, Input, Output,State
import pandas as pd
import utils as ut
import plotly.graph_objects as go

def get_selected_data(figure_brush,x_range,y_range):
        
        x_original = figure_brush['data'][0]['x']
        y_original = figure_brush['data'][0]['y']

        mask = [
                    (x >= x_range[0]) & (x <= x_range[1]) & (y >= y_range[0]) & (y <= y_range[1])
                    for x, y in zip(x_original, y_original)
                ]
                
        x_data = [x for x, include in zip(x_original, mask) if include]
        y_data = [y for y, include in zip(y_original, mask) if include]

        return x_data,y_data



def create_plot_zoom(x_data, y_data, selected_sensor_ref):
    fig = {
        'data': [
            {
                'x': x_data,
                'y': y_data,
                'type': 'line',
                'name': selected_sensor_ref,
                'line': {
                    'color': 'red',  # Cor para a linha principal
                    'width': 2,       # Espessura da linha principal
                }
            }
        ],
        'layout': {
            'autosize': True,
            'margin': {'l': 0, 'r': 10, 't': 0, 'b': 12},
            'plot_bgcolor': 'white',
            'paper_bgcolor': 'gray'
            
        }
    }
    return fig


def create_plot_brush(x0,x1,y0,y1,x_data,y_data,selected_sensor_ref):
    layout = go.Layout(
                dragmode='select',
                selectdirection='h',
                margin={'l': 0, 'r': 0, 't': 0, 'b': 0},
                hovermode='closest',
                xaxis={'title': 'Tempo (s)', 'range': [x0, x1]},
                yaxis={'title': 'Valores', 'range': [y0, y1]},
                newselection=dict(line=dict(color='blue')),
                selections=[
                    dict(
                        x0=(x1/2)-50,
                        x1=(x1/2)+50,
                        y0=y0,
                        y1=y1,
                        type='rect',
                        yref="paper",
                        line=dict(color='blue')
                    )
                ],
                height=100
            )

            # Crie o gráfico
    figure = {
                'data': [
                    {
                        'x': x_data,
                        'y': y_data,
                        'type': 'line',
                        'name': selected_sensor_ref,
                        'line': {
                'color': 'red',  # Cor para a linha principal
                'width': 2,       # Espessura da linha principal
            }
                    }
                ],
                'layout': layout
            }
    return figure




class PlotBrush(html.Div):
    def __init__(self):
        super().__init__([
            dcc.Graph(
                id='line-plot_brush',style={'width': '100%','height':'100px','display': 'inline-block'}
            ),
        dcc.Store(id='stored_data_select_range'),
            
        ], style={'width': '100%', 'display': 'inline-block'})


    def  register_callbacks(self,app):
        # Callback para atualizar o gráfico com base na seleção do dropdown
        @app.callback(
           [ Output('stored_min_max_data', 'data',allow_duplicate=True),
            Output('line-plot_brush', 'figure',allow_duplicate=True),
            Output('line-plot_zoom', 'figure',allow_duplicate=True),
            Output('load-protocol-button', 'disabled',allow_duplicate=True),
            ],
            Input('dropdown_sensor_ref', 'value'),
            State('stored_data_sensores', 'data'),prevent_initial_call=True,
        )
        def create_graph(selected_sensor_ref, data):
            if selected_sensor_ref is None or data is None:
                return dash.no_update,dash.no_update,dash.no_update,dash.no_update

            df = pd.DataFrame(data)
            if selected_sensor_ref not in df.columns:
                return dash.no_update,dash.no_update,dash.no_update,dash.no_update

            x_data = df['sec']  # Ajuste o nome da coluna para o eixo x, se necessário
            y_data = df[selected_sensor_ref]
 
            x0 = min(x_data)
            x1 = max(x_data)
            y0 = min(y_data)
            y1 = max(y_data)
            data_values_min_max={'x0': x0,'x1':x1,'y0': y0,'y1':y1  }

            figure_brush=create_plot_brush(x0,x1,y0,y1,x_data,y_data,selected_sensor_ref)

            x_range=[(x1/2)-50,(x1/2)+50]
            x_data_,y_data_=get_selected_data(figure_brush,x_range,[y0,y1])
            figure_zoom=create_plot_zoom(x_data_,y_data_,selected_sensor_ref)

            figure_brush['layout']['shapes']=ut.update__line_timestamp(x0+(x1-x0)/2,y0,y1)
            figure_zoom['layout']['shapes']=ut.update__line_timestamp(x0+(x1-x0)/2,y0,y1)
            

            return data_values_min_max,figure_brush,figure_zoom,False
        



        @app.callback(
            Output('line-plot_brush', 'figure', allow_duplicate=True),
            Input('dropdown_sensor_optional', 'value'),
            State('stored_data_sensores', 'data'),
            State('line-plot_brush', 'figure'),prevent_initial_call=True,
            )
        def optional_plot(selected_sensor_optional,data,figure):
            if selected_sensor_optional is not None:
                df = pd.DataFrame(data)
                x_data_optional = df['sec']  # Ajuste o nome da coluna para o eixo x, se necessário
                y_data_optional = df[selected_sensor_optional]  # Use selected_sensor_optional em vez de selected_sensor_ref
                fig_brush=figure.copy()
                # Adiciona a linha adicional ao gráfico
                if(len(fig_brush['data'])<2):
                    fig_brush['data'].append({
                        'x': x_data_optional,
                        'y': y_data_optional,
                        'type': 'line',
                        'name': selected_sensor_optional,
                        'line': {
                        'color': 'gray',    # Cor menos suave para a linha opcional
                        'width': 1,        # Linha mais fina para o sensor opcional
                                }
                    })
                else:
                    fig_brush['data'][1]['x'] = x_data_optional
                    fig_brush['data'][1]['y'] = y_data_optional
                    fig_brush['data'][1]['name'] = selected_sensor_optional
                    fig_brush['data'][1]['line'] = {
                        'color': 'gray',  # Cor menos suave para a linha opcional
                        'width': 1,       # Linha mais fina para o sensor opcional
                                }
                
                return fig_brush
            return dash.no_update
            
        @app.callback(
            Output('line-plot_zoom', 'figure', allow_duplicate=True),
            Output('stored_timestamp', 'data', allow_duplicate=True),
            Input('line-plot_brush', 'selectedData'),
            State('stored_data_checkpoint', 'data'),
            State('line-plot_brush', 'figure'),
            State('stored_min_max_data', 'data'),
           
            
            prevent_initial_call=True
        )
        def store_selected_data(selectedData,stored_chek, figure,min_max):
            if selectedData and  'range'  in selectedData:
                x_range = selectedData['range']['x']
                y_range = selectedData['range']['y']

                selected_sensor_ref=figure['data'][0]['name']                
                x_data_,y_data_=get_selected_data(figure,x_range,y_range)
                figure_zoom=create_plot_zoom(x_data_,y_data_,selected_sensor_ref)
                #figure_zoom['layout']['shapes'] =figure['layout']['shapes']
                timestamp = x_range[0] + (x_range[1] - x_range[0]) / 2
                shapes=ut.update__line_timestamp(timestamp,y_range[0],y_range[1])
                df_protocol = pd.DataFrame(stored_chek)
                figure_zoom['layout']['shapes'] =shapes+ut.update_shapes(df_protocol,x_range[0], x_range[1],y_range[0],y_range[1])
                figure_zoom['layout']['annotations'] =ut.update_annotation(df_protocol,x_range[0], x_range[1],y_range[0],y_range[1]) 


                

                return figure_zoom, {"timestamp":timestamp,'type':"select_brush"}
            else:
                return dash.no_update, {"timestamp":min_max['x1']/2,'type':"select_brush"}



        

        @app.callback(
        [Output('log_plot_brush', 'children', allow_duplicate=True),
        Output('line-plot_brush', 'figure', allow_duplicate=True),
        Output('line-plot_zoom', 'figure', allow_duplicate=True),
        Output('change-point-name', 'options', allow_duplicate=True)],
        [Input('stored_data_checkpoint', 'data')],
        [State('stored_timestamp', 'data'),
        State('line-plot_brush', 'figure'),
        State('line-plot_zoom', 'figure'),
        State('stored_min_max_data', 'data')],prevent_initial_call=True,
    )
        def display_df_protocol(data_checkpoint,current_time,figure_brush,figure_zoom,min_max):
            if data_checkpoint is None:
                return "No data loaded yet.",dash.no_update,dash.no_update,dash.no_update
            
            updated_figure_brush = figure_brush.copy()
            
            updated_figure_zoom = figure_zoom.copy()
            df_protocol = pd.DataFrame(data_checkpoint)
            if df_protocol.shape[0] > 0:
                layout=updated_figure_brush['layout']
                

                #annotations=update_annotation(df_protocol)                   
                
                #updated_figure_zoom['layout']['annotations']=annotations
            
                shapes=ut.update__line_timestamp(current_time['timestamp'],min_max['y0'],min_max['y1']/2)
                layout['shapes'] =shapes+ut.update_shapes(df_protocol,None, None,min_max['y0'],min_max['y1']/2)
                updated_figure_brush['layout']=layout
                #points=[min(figure_zoom["data"][0]),max(figure_zoom["data"][0])]
                #updated_figure_zoom['data'][0]
                if 'shapes' not in figure_zoom['layout']:
                        figure_zoom['layout']['shapes'] = []
                selections=layout['selections'][0]
                shapes_zoom=ut.update__line_timestamp(current_time['timestamp'],selections['y0'],selections['y1'])
                updated_figure_zoom['layout']['shapes']=shapes_zoom+ut.update_shapes(df_protocol,selections['x0'], selections['x1'],selections['y0'],selections['y1'])
                updated_figure_zoom['layout']['annotations'] =ut.update_annotation(df_protocol,selections['x0'], selections['x1'],selections['y0'],selections['y1']) 
                
                

                unique_names = df_protocol['change_point_name'].unique()
                        # Construa a lista de opções para o dropdown
                options = [{'label': name, 'value': name} for name in unique_names]
                return html.Div([
                    html.H5(f'DataFrame Loaded: {len(df_protocol)}   point rows'),
                    
                ]),updated_figure_brush, updated_figure_zoom,options
            else:
                return "No data loaded yet.",dash.no_update,dash.no_update,dash.no_update
            

            