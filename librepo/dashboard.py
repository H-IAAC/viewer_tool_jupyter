import dash
import dash_html_components as html
from dash.dependencies import Input, Output, State


class DashboardApp:
    def __init__(self):
        self.app = dash.Dash(__name__)
        self.components = []  # Store the added components
        self.app.layout = html.Div(self.components)
        self.video_urls = []  # Store video URLs and corresponding IDs
        
        

    def run(self, host="127.0.0.1", port=8060):
        self.app.run_server(host=host, port=port, dev_tools_ui=True,     debug=True,     dev_tools_hot_reload=True,
    threaded=True)
        
    def add_component(self, component, orientation='vertical',width='100%',height='100%'):
            
        if orientation == 'vertical':
            self.components.append(html.Div(component, style={'width': width}))
        elif orientation == 'horizontal':
            self.components.append(html.Div(component, style={'display': 'inline-block','width': width}))
        else:
            raise ValueError("Invalid orientation. Use 'vertical' or 'horizontal'.")
            
    def add_callback_video_seekTo_click_graph(self,video,graph):
        self.app.callback(
            Output(video.id, 'seekTo'),
            Input(graph.id, 'clickData'),
            State(video.id, 'duration')
        )(video.update_video_time)
        
        
        
    def add_callback_video_scatter_update(self,graph,video):
        self.app.callback(
                Output(graph.id, 'figure'),
                Input(video.id, 'currentTime')
            )(graph.update_scatter_plot)
        
        
    def add_callback_graph_update_vLine(self,graph,video):
        self.app.callback(
                Output(graph.id, 'figure'),
                Input(video.id, 'currentTime')
            )(graph.add_vLine)
        
        
        



        
    
   

 