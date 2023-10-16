from dash.dependencies import Input, Output, State
import dash
from dash import html


class DashboardApp:
    def __init__(self):
        self.app = dash.Dash(__name__)
        self.components = []  # Store the added components
        self.app.layout = html.Div(self.components)
        self.video_count = 0

    def _get_video_url(self):
        self.video_count += 1
        return "/video" + str(self.video_count)

    def add_component(self, component):
        self.components.append(component)

    def linear_register_callbacks(self, graph):
        self.app.callback(
            Output(graph.id, "figure"),
            Output(f"{graph.id}-vertical-line-slider", "min"),
            Output(f"{graph.id}-vertical-line-slider", "max"),
            Output(f"{graph.id}-vertical-line-slider", "marks"),
            Input(graph.id, "relayoutData"),
            Input(f"{graph.id}-max-points-input", "value"),
            Input(f"{graph.id}-x-axis-start-input", "value"),
            Input(f"{graph.id}-x-axis-end-input", "value"),
            Input(f"{graph.id}-vertical-line-slider", "value"),  # Use graph.id here
        )(graph.update_with_relayout)

    def add_callback_click_graph_seekTo_video(self, graph, video):
        self.app.callback(
            Output(video.id, "seekTo", allow_duplicate=True),
            Input(graph.id, "clickData"),
            State(video.id, "duration"),
            prevent_initial_call=True,
        )(self.update_video_time)

    def update_video_time(self, click_data, video_duration):
        if click_data and click_data["points"]:
            x_click = click_data["points"][0]["x"]
            video_time = min(x_click, video_duration or 0)
            return video_time
        else:
            ctx = dash.callback_context
            if ctx.triggered:
                prop_id = ctx.triggered[0]["prop_id"].split(".")[0]
                if prop_id == self.id:
                    return dash.no_update
            return 0.0

    def add_callback_timestamp_video_verticalline_graph(self, graph, video):
        @self.app.callback(
            Output(f"{graph.id}-vertical-line-slider", "value"),
            Input(video.id, "currentTime"),
        )
        def update_slider_value(input_value):
            return input_value

    def run(self, port=8997):
        self.app.run_server(
            port=port,
            dev_tools_ui=True,
            debug=False,
            dev_tools_hot_reload=True,
            threaded=True,
        )
