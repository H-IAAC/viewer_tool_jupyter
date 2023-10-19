import dash_bootstrap_components as dbc
from dash import dcc, html, no_update, callback_context
from dash.dependencies import Input, Output, State


class _InputLabel(html.Div):
    def __init__(self, label, value):
        super().__init__()
        self.label = html.Label(label, style={"margin-right": 5})
        self.input = dcc.Input(type="number", value=value)

        self.children = [self.label, self.input]


class Controller(html.Div):
    def __init__(self, app, width="100%", **kwargs):
        super().__init__(**kwargs)

        self.app = app.app
        self.button_icon = html.I(className="bi-play-fill")
        self.isPlaying = False
        self.start_stop_button = dbc.Button(
            [self.button_icon],
            className="btn btn-secondary",
            style={"margin-bottom": 10},
        )
        self.start_input = _InputLabel("Start: ", 0)
        self.end_input = _InputLabel("End: ", 0)
        self.slider = dcc.Slider(
            min=0,
            max=100,
            step=1,
            value=0,
            marks=None,
            tooltip={"placement": "bottom", "always_visible": True},
        )
        self.children = [
            self.start_stop_button,
            html.Div(
                [
                    self.start_input,
                    html.Div(style={"width": 30}),
                    self.end_input,
                ],
                style={
                    "display": "flex",
                    "margin-top": 10,
                    "margin-bottom": 10,
                },
            ),
            self.slider,
        ]
        self.style = {
            "margin": 10,
            "padding": 10,
            "border": "1px solid #ccc",
            "border-radius": 8,
            "width": width,
        }

    def connectToVideo(self, video):
        self.video_player = video

        def _set_duration(duration):
            if duration == 0 or duration == None:
                return no_update, no_update
            self.duration = duration
            return duration, duration

        # Callback to set video duration time to slider
        self.app.callback(
            Output(self.end_input.input, "value", allow_duplicate=True),
            Output(self.slider, "max", allow_duplicate=True),
            Input(self.video_player, "duration"),
            prevent_initial_call=True,
        )(_set_duration)

        def _set_current_time(drag_value):
            if self.isPlaying:
                return no_update
            return drag_value

        # Callback to set video current time when slider is dragged
        self.app.callback(
            Output(self.video_player, "seekTo"), Input(self.slider, "drag_value")
        )(_set_current_time)

        def _set_start_end_value(start_value, end_value):
            if start_value == None or end_value == None:
                return no_update, no_update
            return start_value, end_value

        # Callback to set slider min and max value
        self.app.callback(
            Output(self.slider, "min", allow_duplicate=True),
            Output(self.slider, "max", allow_duplicate=True),
            Input(self.start_input.input, "value"),
            Input(self.end_input.input, "value"),
            prevent_initial_call=True,
        )(_set_start_end_value)

        def _check_start_end_value(start_value, end_value):
            if start_value == None or end_value == None:
                return no_update, no_update
            if start_value > end_value - 2:
                return (end_value - 2), no_update
            elif end_value < start_value + 2:
                return no_update, start_value + 2
            elif start_value < 0:
                return 0, no_update
            elif end_value > self.duration:
                return no_update, self.duration
            return no_update, no_update

        # Callback that make start and end values stay within boundries
        self.app.callback(
            Output(self.start_input.input, "value", allow_duplicate=True),
            Output(self.end_input.input, "value", allow_duplicate=True),
            Input(self.start_input.input, "value"),
            Input(self.end_input.input, "value"),
            prevent_initial_call=True,
        )(_check_start_end_value)

        def _loop_in_boundries(start_value, end_value, currentTime):
            if start_value == None or end_value == None:
                return no_update
            if currentTime == None:
                return no_update
            if currentTime < end_value:
                return no_update
            return start_value

        # Callback loop video between start and end
        self.app.callback(
            Output(self.video_player, "seekTo", allow_duplicate=True),
            Input(self.start_input.input, "value"),
            Input(self.end_input.input, "value"),
            Input(self.video_player, "currentTime"),
            prevent_initial_call=True,
        )(_loop_in_boundries)

        def _start_stop_play(n_clicks):
            if n_clicks == 0 or n_clicks == None:
                return no_update, no_update, no_update
            if self.isPlaying:
                self.isPlaying = False
                return "bi-play-fill", False, False
            self.isPlaying = True
            return "bi-pause-fill", True, True

        self.app.callback(
            Output(self.button_icon, "className"),
            Output(self.video_player, "playing"),
            Output(self.slider, "disabled"),
            Input(self.start_stop_button, "n_clicks"),
        )(_start_stop_play)

        def _update_slider(currentTime):
            if not self.isPlaying:
                return no_update
            return currentTime

        self.app.callback(
            Output(self.slider, "value"), Input(self.video_player, "currentTime")
        )(_update_slider)

    def addGraph(self, graph):
        self.children.append(graph)

        self.app.callback(
            Output(graph.graph, "figure"),
            Input(self.video_player, "currentTime"),
        )(graph.update_vertical_line)

        self.app.callback(
            Output(graph.graph, "figure", allow_duplicate=True),
            Input(self.start_input.input, "value"),
            Input(self.end_input.input, "value"),
            prevent_initial_call=True,
        )(graph.update_traces)

        self.app.callback(
            Output(self.start_input.input, "value", allow_duplicate=True),
            Output(self.end_input.input, "value", allow_duplicate=True),
            Input(graph.graph, "relayoutData"),
            prevent_initial_call=True,
        )(graph.update_start_end)

        def _update_video_time(click_data, video_duration):
            if click_data and click_data["points"]:
                x_click = click_data["points"][0]["x"]
                video_time = min(x_click, video_duration or 0)
                return video_time, video_time
            else:
                ctx = callback_context
                if ctx.triggered:
                    prop_id = ctx.triggered[0]["prop_id"].split(".")[0]
                    if prop_id == self.id:
                        return no_update, no_update
                return 0.0, 0.0

        self.app.callback(
            Output(self.video_player, "seekTo", allow_duplicate=True),
            Output(self.slider, "value", allow_duplicate=True),
            Input(graph.graph, "clickData"),
            State(self.video_player, "duration"),
            prevent_initial_call=True,
        )(_update_video_time)
