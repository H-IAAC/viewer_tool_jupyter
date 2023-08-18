import dash_player
from flask import Flask, send_file
from dash import dcc, html


class VideoPlayer(dash_player.DashPlayer):
    def __init__(self, app, server, id, video_path,width,height, **kwargs):
        super().__init__(**kwargs)
        self.id = id
        self.video_path = video_path
        self.url = "/" + id
        self.server = server
        self.app = app
        self.width=width
        self.height=height

        #self.style = {'width': '100%', 'height': '100%', 'object-fit': 'contain'}  # Defina o estilo para ocupar 100% em largura e altura

        self.server.add_url_rule(self.url, f'serve_video_{self.url}', self.serve_video, methods=['GET'])

    def serve_video(self):
        return send_file(self.video_path, mimetype='video/mp4')

    def get_layout(self):
        
        return self # The LinearPlot object itself


        