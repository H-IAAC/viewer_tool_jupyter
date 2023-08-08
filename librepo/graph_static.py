import dash_core_components as dcc
import plotly.graph_objs as go

class MultiTracePlot(dcc.Graph):
    def __init__(self,  id, **kwargs):
        super().__init__(id=id, **kwargs)
    
        self.traces = []
        self.fig={}

    def add_trace(self, df, name, column):
        trace = go.Scatter(x=df['Timestamp'], y=df[column], mode='lines', name=f'{name} - {column}')
        self.traces.append(trace)

    def show_plot(self):
        layout = go.Layout(title='Gráfico com Múltiplos Traces')
        self.fig = go.Figure(data=self.traces, layout=layout)
        self.fig.update_layout(showlegend=True)
        self.fig.show()
    def get_figure(self):
        return self.fig
