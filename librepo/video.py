import dash_player
from dash import dcc, html, no_update
from dash.dependencies import Input, Output
from flask import send_file


class VideoPlayer(dash_player.DashPlayer):
    def __init__(
        self,
        app,
        video_path,
        width="100%",
        height="100%",
        playing=True,
        intervalCurrentTime=1000,
        **kwargs,
    ):
        super().__init__(
            playing=playing,
            intervalCurrentTime=intervalCurrentTime,
            **kwargs,
        )
        self.loop = False
        self.controls = True
        self.width = width
        self.height = height
        self.video_path = video_path
        self.url = app._get_video_url()
        self.server = app.app.server

        self.server.add_url_rule(
            self.url, f"serve_video_{self.url}", self.serve_video, methods=["GET"]
        )

    def serve_video(self):
        return send_file(self.video_path, mimetype="video/mp4")

    def get_layout(self):
        return self  # The LinearPlot object itself
