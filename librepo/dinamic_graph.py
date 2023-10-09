import pandas as pd
from dash import dcc, html
import plotly.graph_objs as go

class LinearPlot(dcc.Graph):
    def __init__(self, data_df, x_col, y_cols, max_points=100, id='linear-plot', title='', **kwargs):  
        super().__init__(id=id, **kwargs)
        self.data_df = data_df
        self.x_col = x_col
        self.y_cols = y_cols
        self.max_points = max_points
        self.vertical_line_x = None
        self.layout = self.get_layout()
        self.title = title  # Nuevo parámetro para el título
        self.figure = self.create_figure()
        self.style = {'width': '100%', 'height': '40vh'}
        
        # Register callbacks
        #self.register_callbacks()

    def get_layout(self):
        return html.Div([
            self,
            html.Div([
                html.Label("Max Points:"),
                dcc.Input(id=f'{self.id}-max-points-input', type='number', value=self.max_points,
                          style={'width': '15%', 'display': 'inline-block'}),
                html.Label("X->start-end:", style={'width': '25%', 'display': 'inline-block'}),
                dcc.Input(id=f'{self.id}-x-axis-start-input', type='number', value=0, style={'width': '15%', 'display': 'inline-block'}),
                dcc.Input(id=f'{self.id}-x-axis-end-input', type='number', value=self.data_df[self.x_col].max(),
                          style={'width': '20%', 'display': 'inline-block'}),
            ], style={'display': 'flex', 'margin-top': '10px'}),
            dcc.Slider(
                id=f'{self.id}-vertical-line-slider',
                min=self.data_df[self.x_col].min(),
                max=self.data_df[self.x_col].max(),
                step=10,
                value=self.data_df[self.x_col].min(),
                marks={
                    self.data_df[self.x_col].min(): {'label': str(self.data_df[self.x_col].min()), 'style': {'display': 'none'}},
                    self.data_df[self.x_col].max(): {'label': str(self.data_df[self.x_col].max()), 'style': {'display': 'none'}},
                },
                tooltip={'placement': 'bottom', 'always_visible': True}
            ),
        ])

    def create_figure(self):
        fig = go.Figure()
        fig.update_layout(margin={'l': 0, 'r': 0, 't': 25, 'b': 0},title={'text': self.title, 'x': 0.5})
        

        for y_col in self.y_cols:
            trace = go.Scatter(x=self.data_df[self.x_col], y=self.data_df[y_col], mode='lines', name=y_col)
            fig.add_trace(trace)

        return fig

    def update_traces(self, xaxis_range):
        filtered_df = self.data_df[(self.data_df[self.x_col] >= xaxis_range[0]) & (self.data_df[self.x_col] <= xaxis_range[1])]
        step = len(filtered_df) // self.max_points if len(filtered_df) > self.max_points else 1
        sampled_df = filtered_df.iloc[::step]

        with self.figure.batch_update():
            for trace in self.figure.data:
                y_col = trace.name
                trace.x = sampled_df[self.x_col]
                trace.y = sampled_df[y_col]

    def update_vertical_line(self, vertical_line_x):
        vertical_line = {
            'type': 'line',
            'x0': vertical_line_x,
            'x1': vertical_line_x,
            'y0': 0,
            'y1': 1,
            'xref': 'x',
            'yref': 'paper',
            'line': {
                'dash': 'dot',
                'color': 'red',
                'width': 2,
            },
        }
        with self.figure.batch_update():
            self.figure.layout.shapes = [vertical_line]

    def update_with_relayout(self, relayoutData, max_points, x_axis_start, x_axis_end, vertical_line_value):
        xaxis_range = relayoutData['xaxis.range'] if relayoutData and 'xaxis.range' in relayoutData else [x_axis_start, x_axis_end]
        self.max_points = max_points
        self.update_traces(xaxis_range)
        self.update_vertical_line(vertical_line_value)
        print("foi")
        minV = max(self.data_df[self.x_col].min(), x_axis_start)
        maxV = min(self.data_df[self.x_col].max(), x_axis_end)
        marks={
                    minV: {'label': str(minV), 'style': {'display': 'none'}},
                    maxV: {'label': str(maxV), 'style': {'display': 'none'}},
                }
        return self.figure, minV, maxV, marks
 