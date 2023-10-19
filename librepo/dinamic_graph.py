import plotly.graph_objs as go
from dash import dcc, html, no_update
from dash.dependencies import Input, Output


class LinearPlot(html.Div):
    def __init__(self, app, data_df, x_col, y_cols, max_points=100, title="", **kwargs):
        super().__init__(**kwargs)
        self.app = app.app
        self.data_df = data_df
        self.x_col = x_col
        self.y_cols = y_cols
        self.title = title

        self.x_axis_start = 0
        self.x_axis_end = 0
        self.filtered_data = self._get_filtered_data(max_points)

        self.graph = dcc.Graph(
            figure=self.create_figure(),
            style={"width": "100%", "height": "40vh"},
        )
        self.max_points = dcc.Input(
            type="number",
            value=max_points,
            style={"width": "15%", "display": "inline-block"},
        )

        self.children = [
            self.graph,
            html.Div(
                [
                    html.Label("Max Points:", style={"margin-right": 5}),
                    self.max_points,
                ],
                style={"display": "flex", "margin-top": "10px"},
            ),
        ]

        def _filter_max_points(max_points):
            self.filtered_data = self._get_filtered_data(max_points)

            with self.graph.figure.batch_update():
                for trace in self.graph.figure.data:
                    y_col = trace.name
                    trace.x = self.filtered_data[self.x_col]
                    trace.y = self.filtered_data[y_col]
            return self.graph.figure

        self.app.callback(
            Output(self.graph, "figure", allow_duplicate=True),
            Input(self.max_points, "value"),
            prevent_initial_call=True,
        )(_filter_max_points)
        
    def _get_filtered_data(self, max_points):
        step = (
                len(self.data_df) // max_points if len(self.data_df) > max_points else 1
            )
        return self.data_df.iloc[::step]


    def create_figure(self):
        fig = go.Figure()
        fig.update_layout(
            margin={"l": 0, "r": 0, "t": 25, "b": 0},
            title={"text": self.title, "x": 0.5},
        )

        for y_col in self.y_cols:
            trace = go.Scatter(
                x=self.filtered_data[self.x_col],
                y=self.filtered_data[y_col],
                mode="lines",
                name=y_col,
            )
            fig.add_trace(trace)

        return fig

    def update_traces(self, x_axis_start, x_axis_end):
        if x_axis_start == self.x_axis_start and x_axis_end == self.x_axis_end:
            return no_update

        filtered_df = self.filtered_data[
            (self.filtered_data[self.x_col] >= x_axis_start)
            & (self.filtered_data[self.x_col] <= x_axis_end)
        ]

        with self.graph.figure.batch_update():
            for trace in self.graph.figure.data:
                y_col = trace.name
                trace.x = filtered_df[self.x_col]
                trace.y = filtered_df[y_col]
        return self.graph.figure

    def update_start_end(self, relayoutData):
        if (
            relayoutData
            and "xaxis.range[0]" in relayoutData
            and "xaxis.range[1]" in relayoutData
        ):
            self.x_axis_start = relayoutData["xaxis.range[0]"]
            self.x_axis_end = relayoutData["xaxis.range[1]"]
            return relayoutData["xaxis.range[0]"], relayoutData["xaxis.range[1]"]
        elif relayoutData and "xaxis.autorange" in relayoutData:
            return 0, self.filtered_data[self.x_col].max()
        else:
            return no_update, no_update

    def update_vertical_line(self, vertical_line_x):
        if vertical_line_x == None or self.graph.figure == None:
            return no_update
        if vertical_line_x == None:
            return
        vertical_line = {
            "type": "line",
            "x0": vertical_line_x,
            "x1": vertical_line_x,
            "y0": 0,
            "y1": 1,
            "xref": "x",
            "yref": "paper",
            "line": {
                "dash": "dot",
                "color": "red",
                "width": 2,
            },
        }
        with self.graph.figure.batch_update():
            self.graph.figure.layout.shapes = [vertical_line]
        self.graph.figure.layout.uirevision = "1"
        return self.graph.figure
