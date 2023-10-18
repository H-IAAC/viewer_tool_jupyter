from librepo.controller import Controller
from librepo.dinamic_graph import LinearPlot
from librepo.dashboard import DashboardApp
import pandas as pd

from librepo.layouts import HorizontalLayout
from librepo.video import VideoPlayer


def main():
    csv_file_name = (
        "noteboks/Data/public_dataset/acc_sitting_csv/acc_sitting_upperarm.csv"
    )
    acc_sitting_upperarm = pd.read_csv(csv_file_name)
    acc_sitting_upperarm.head
    acc_sitting_upperarm["VideoTimelapse"] = [
        x - acc_sitting_upperarm["attr_time"][0]
        for x in acc_sitting_upperarm["attr_time"]
    ]
    acc_sitting_upperarm["sec"] = [
        x / 1000 for x in acc_sitting_upperarm["VideoTimelapse"]
    ]
    acc_sitting_upperarm[0:4]

    csv_file_name = "noteboks/Data/public_dataset/acc_sitting_csv/acc_sitting_shin.csv"
    acc_sitting_shin = pd.read_csv(csv_file_name)
    acc_sitting_shin.head
    acc_sitting_shin["VideoTimelapse"] = [
        x - acc_sitting_shin["attr_time"][0] for x in acc_sitting_shin["attr_time"]
    ]
    acc_sitting_shin["sec"] = [x / 1000 for x in acc_sitting_shin["VideoTimelapse"]]

    app = DashboardApp()

    player = VideoPlayer(
        app,
        video_path="../noteboks/Data/public_dataset/video_sitting.webm",
        volume=0.0,
    )
    controller = Controller(app)
    controller.connectToVideo(player)

    # acc_sitting_upperarm = LinearPlot(data_df=acc_sitting_upperarm, x_col='sec', y_cols=['attr_x', 'attr_y', 'attr_z'],
    #                                    max_points=50, id='linear-plot',title='acc sitting upperarm')

    # acc_sitting_shin = LinearPlot(data_df=acc_sitting_shin, x_col='sec', y_cols=['attr_x', 'attr_y', 'attr_z'],
    #                                max_points=50, id='acc_sitting_shin',title='acc sitting shin')

    # vertical_layout = VerticalLayout()
    # vertical_layout.append(acc_sitting_shin)
    # vertical_layout.append(acc_sitting_upperarm)

    horizontal_layout = HorizontalLayout()
    horizontal_layout.append(player)
    horizontal_layout.append(controller)
    
    
    # horizontal_layout.append(vertical_layout)

    app.add_component(horizontal_layout)

    # # Registrar eventos y callbacks
    # app.linear_register_callbacks(acc_sitting_shin)
    # app.add_callback_click_graph_seekTo_video(acc_sitting_shin, player)
    # app.add_callback_timestamp_video_verticalline_graph(acc_sitting_shin, player)

    # app.linear_register_callbacks(acc_sitting_upperarm)
    # app.add_callback_timestamp_video_verticalline_graph(acc_sitting_upperarm, player)
    # app.add_callback_click_graph_seekTo_video(acc_sitting_upperarm, player)

    app.run()


if __name__ == "__main__":
    main()
