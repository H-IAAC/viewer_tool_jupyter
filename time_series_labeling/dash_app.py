import yaml
from dash import Dash, dcc, html
from layout.load_protocol import LoadProtocol
from layout.zoom import LoadZoom
from layout.brush import PlotBrush
from layout.video import VideoPlayer
from layout.controls_load_data import ControlsLoadData
from layout.control_timestamp import ControlsTimestamp
from layout.control_chekpoint import ControlsChekpoint

class DashApp:
    def __init__(self, config_path='config.yaml'):
        self.config = self._load_config(config_path)
        self.app = Dash(__name__)
        self._create_layout()
        self._register_callbacks()

    def _load_config(self, config_path):
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)

    def _create_layout(self):
        controls_load_data_sensors = ControlsLoadData()
        plot_brush = PlotBrush()
        control_chekpoint = ControlsChekpoint(self.config)
        load_zoom_layout = LoadZoom()
        video_player = VideoPlayer(id_upload='upload-video', id_output='output-video-player')
        load_data_activities_layout = LoadProtocol()
        controls_timestamp = ControlsTimestamp()

        # Utilizando as cores e padding do arquivo de configuração
        self.app.layout = html.Div([
            html.Div([
                # Coluna à esquerda com 'control_chekpoint' e 'load_zoom_layout'
                html.Div([
                    control_chekpoint,
                    load_zoom_layout
                ], style={
                    'width': '70%', 
                    'display': 'flex', 
                    'flexDirection': 'column', 
                    'justifyContent': 'flex-start',
                    'boxSizing': 'border-box',
                    'maxHeight': self.config['layout']['max_height'],  
                    'overflow': 'hidden'  
                }),
                
                # Coluna à direita com o 'video_player'
                html.Div([
                    html.Div(video_player, style={
                        'width': self.config['video_player']['width'], 
                        'height': self.config['video_player']['height'],
                        'maxHeight': self.config['layout']['max_height'],  
                        'overflow': 'hidden',
                        'alignSelf': 'flex-start',
                        'boxSizing': 'border-box'
                    })
                ], style={
                    'width': '30%', 
                    'display': 'flex',
                    'alignItems': 'flex-start',
                    'boxSizing': 'border-box'
                }),
            ], style={
                'display': 'flex',
                'width': '100%'
            }),
            
            # Outras seções
            html.Div([
                controls_load_data_sensors,
                plot_brush,
                controls_timestamp,
                load_data_activities_layout,
            ], style={'display': 'flex', 'flexDirection': 'column'}),
        
            dcc.Store(id='stored_timestamp'),
            
        ], style={
            'backgroundColor': self.config['layout']['background_color'], 
            'padding': self.config['layout']['padding'], 
            'boxSizing': 'border-box',
            'color': self.config['layout']['font_color']  # Cor da fonte
        })

    def _register_callbacks(self):
        controls_load_data_sensors = ControlsLoadData()
        plot_brush = PlotBrush()
        load_data_activities_layout = LoadProtocol()
        load_zoom_layout = LoadZoom()
        controls_timestamp = ControlsTimestamp()
        video_player = VideoPlayer(id_upload='upload-video', id_output='output-video-player')

        controls_load_data_sensors.register_callbacks(self.app)  
        plot_brush.register_callbacks(self.app)
        load_data_activities_layout.register_callbacks(self.app)  
        load_zoom_layout.register_callbacks(self.app)  
        controls_timestamp.register_callbacks(self.app)
        video_player.register_callbacks(self.app)

    def start(self):
        # Utilizando a porta e modo de depuração do arquivo de configuração
        self.app.run_server(
            port=self.config['server']['port'], 
            debug=self.config['server']['debug'],dev_tools_hot_reload=False,
        )

    def stop(self):
        # Dash doesn't have a built-in stop method, but you can handle this externally.
        pass

