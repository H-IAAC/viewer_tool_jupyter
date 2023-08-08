import dash_core_components as dcc
import plotly.graph_objs as go
import numpy as np
from plotly.graph_objs import Scatter


class ScatterPlot(dcc.Graph):
    def __init__(self, data, id, **kwargs):
        super().__init__(id=id, **kwargs)
        self.data = data

    def update_scatter_plot(self, current_time):
        num_samples = len(self.data)
        current_sample = int(current_time) if current_time is not None else 0
        marker_sizes = [20 if i == current_sample else 10 for i in range(num_samples)]

        data = [
            go.Scatter(
                x=self.data['x'],
                y=self.data['y'],
                mode='markers',
                marker=dict(size=marker_sizes),
                text=list(range(num_samples)),
                hoverinfo='text',
            )
        ]

        layout = go.Layout(
            title='Gráfico de Dispersión',
            xaxis=dict(title='x'),
            yaxis=dict(title='y'),
            showlegend=False
        )

        return {'data': data, 'layout': layout}  
    



import plotly.graph_objects as go
import dash_core_components as dcc

class LinearPlot(dcc.Graph):
    def __init__(self, data, id, **kwargs):
        super().__init__(id=id, **kwargs)
        self.figure = go.Figure(data=data)
        self.data=self.figure.data
        self.vline=None
    
    def add_trace(self, trace):
        """
        Adiciona um traço ao gráfico.
        
        Args:
            trace: Um objeto trace contendo as informações do traço.
        """
        self.figure.add_trace(trace) 
        
    def add_lines_from_df(self,df,x,y=[]):
        for line in y:                  
            trace=Scatter(x=df[x], y=df[line], name=line)
            self.add_trace(trace)
        
        
        
        

        

    
    def update_trace(self, trace_id, trace):
        """
        Atualiza o traço com o ID fornecido com as propriedades do traço fornecido.
        
        Args:
            trace_id: O ID do traço a ser atualizado (como uma string).
            trace: Um objeto trace contendo as informações do traço a ser atualizado.
        """
        for i, existing_trace in enumerate(self.figure.data):
            if existing_trace.name == trace_id:
                self.figure.data[i].update(trace)
                break
                
                
    def update_graph(self,start_time, end_time):
        selected_datetimes = []
        selected_values = []

        for dt, value in zip(self.data[0].x, self.data[0].y):
            if start_time <= dt <= end_time:
                selected_datetimes.append(dt)
                selected_values.append(value)

        self.figure.data[0].x = selected_datetimes
        self.figure.data[0].y = selected_values  
        
    
    def update_graph_currentTime(self,currentTime):
        windows_size=10
        selected_datetimes = []
        selected_values = []
        start_time=0
        end_time=100
        

        for dt, value in zip(self.data[0].x, self.data[0].y):
            if start_time <= dt <= end_time:
                selected_datetimes.append(dt)
                selected_values.append(value)

        self.figure.data[0].x = selected_datetimes
        self.figure.data[0].y = selected_values  
                

    def add_vLine(self, pos_x):
        current_sample = int(pos_x) if pos_x is not None else 0
        if self.vline is not None:
            shapes_list = list(self.figure.layout.shapes)
            shapes_list.remove(self.vline)
            self.figure.layout.shapes = tuple(shapes_list)

        self.vline = go.layout.Shape(
            type="line",
            x0=pos_x,
            y0=np.min(self.data[0].y),
            x1=pos_x,
            y1=np.max(self.data[0].y),
            line=dict(
                color="green",
                width=3,
                dash="dash",
            ),
        )
        shapes_list = list(self.figure.layout.shapes)
        shapes_list.append(self.vline)
        self.figure.layout.shapes = tuple(shapes_list)     

        
    