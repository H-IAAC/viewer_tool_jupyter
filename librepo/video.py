import dash_player
from flask import Flask, send_file


class VideoPlayer(dash_player.DashPlayer):
    def __init__(self, app, server, id, video_path, **kwargs):
        super().__init__(**kwargs)
        self.id = id
        self.video_path = video_path
        self.url = "/" + id
        self.server = server
        self.app = app

        self.server.add_url_rule(self.url, f'serve_video_{self.url}', self.serve_video, methods=['GET'])

    def serve_video(self):
        return send_file(self.video_path, mimetype='video/mp4')

    def add_to_layout(self):
        return self  # Return the instance of the VideoPlayer