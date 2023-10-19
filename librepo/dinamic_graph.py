import pandas as pd
from dash import dcc, html, no_update
import plotly.graph_objs as go


class LinearPlot(html.Div):
    def __init__(self, data_df, x_col, y_cols, max_points=100, title="", **kwargs):
        super().__init__(**kwargs)
        self.data_df = data_df
        self.x_col = x_col
        self.y_cols = y_cols
        self.max_points = max_points
        self.title = title

        self.x_axis_start = 0
        self.x_axis_end = 0

        self.graph = dcc.Graph(
            figure=self.create_figure(),
            style={"width": "100%", "height": "40vh"},
        )

        self.children = [
            self.graph,
            html.Div(
                [
                    html.Label("Max Points:", style={"margin-right": 5}),
                    dcc.Input(
                        type="number",
                        value=self.max_points,
                        style={"width": "15%", "display": "inline-block"},
                    ),
                ],
                style={"display": "flex", "margin-top": "10px"},
            ),
        ]

    def create_figure(self):
        fig = go.Figure()
        fig.update_layout(
            margin={"l": 0, "r": 0, "t": 25, "b": 0},
            title={"text": self.title, "x": 0.5},
        )

        for y_col in self.y_cols:
            trace = go.Scatter(
                x=self.data_df[self.x_col],
                y=self.data_df[y_col],
                mode="lines",
                name=y_col,
            )
            fig.add_trace(trace)

        return fig

    def update_traces(self, x_axis_start, x_axis_end):
        if x_axis_start == self.x_axis_start and x_axis_end == self.x_axis_end:
            return no_update

        filtered_df = self.data_df[
            (self.data_df[self.x_col] >= x_axis_start)
            & (self.data_df[self.x_col] <= x_axis_end)
        ]
        # step = (
        #     len(filtered_df) // self.max_points
        #     if len(filtered_df) > self.max_points
        #     else 1
        # )
        # sampled_df = filtered_df.iloc[::step]

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
            return 0, self.data_df[self.x_col].max()
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

    def update_with_relayout(
        self, relayoutData, max_points, x_axis_start, x_axis_end, vertical_line_value
    ):
        xaxis_range = (
            relayoutData["xaxis.range"]
            if relayoutData and "xaxis.range" in relayoutData
            else [x_axis_start, x_axis_end]
        )
        self.max_points = max_points
        self.update_traces(xaxis_range)
        self.update_vertical_line(vertical_line_value)
        minV = max(self.data_df[self.x_col].min(), x_axis_start)
        maxV = min(self.data_df[self.x_col].max(), x_axis_end)
        marks = {
            minV: {"label": str(minV), "style": {"display": "none"}},
            maxV: {"label": str(maxV), "style": {"display": "none"}},
        }
        return self.graph.figure, minV, maxV, marks
