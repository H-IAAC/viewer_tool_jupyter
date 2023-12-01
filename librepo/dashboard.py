import dash
import dash_bootstrap_components as dbc
from dash import html
from dash.dependencies import Input, Output, State


class DashboardApp:
    def __init__(self):
        self.app = dash.Dash(
            __name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP]
        )
        self.components = []  # Store the added components
        self.app.layout = html.Div(self.components)
        self.video_count = 0

    def _get_video_url(self):
        self.video_count += 1
        return "/video" + str(self.video_count)

    def add_component(self, component):
        self.components.append(component)

    def run(self, port=8997):
        self.app.run_server(
            port=port,
            host='0.0.0.0',
            dev_tools_ui=True,
            debug=False,
            dev_tools_hot_reload=True,
            threaded=True,
        )
