from dash import dcc, html, no_update
from dash.dependencies import Input, Output

class _InputLabel(html.Div):
    def __init__(self, label, value):
        super().__init__()
        self.label = html.Label(label)
        self.input = dcc.Input(type="number", value=value)

        self.children = [self.label, self.input]
        
class Controller(html.Div):
    def __init__(self, app):
        super().__init__()

        self.app = app.app
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
            html.Div([html.Label("X-axis:", style={"font-weight": "bold"})]),
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
            return drag_value

        # Callback to set video current time when slider is dragged
        self.app.callback(
            Output(self.video_player, "seekTo"), Input(self.slider, "drag_value")
        )(_set_current_time)

        def _set_min_max_value(start_value, end_value):
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
        )(_set_min_max_value)

        def _check_min_max_value(start_value, end_value):
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

        # Callback that make min and max values stay within boundries
        self.app.callback(
            Output(self.start_input.input, "value", allow_duplicate=True),
            Output(self.end_input.input, "value", allow_duplicate=True),
            Input(self.start_input.input, "value"),
            Input(self.end_input.input, "value"),
            prevent_initial_call=True,
        )(_check_min_max_value)

        def _loop_in_boundries(start_value, end_value, currentTime):
            if start_value == None or end_value == None:
                return no_update
            if currentTime == None:
                return no_update
            if currentTime < end_value:
                return no_update
            return start_value

        # Callback loop video between min and max
        self.app.callback(
            Output(self.video_player, "seekTo", allow_duplicate=True),
            Input(self.start_input.input, "value"),
            Input(self.end_input.input, "value"),
            Input(self.video_player, "currentTime"),
            prevent_initial_call=True,
        )(_loop_in_boundries)
