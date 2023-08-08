import dash_player
import dash_html_components as html
from moviepy.editor import VideoFileClip
import dash
from moviepy.editor import VideoFileClip
import dash_player

class VideoPlayer(dash_player.DashPlayer):
    def __init__(
        self,
        id=None,
        className=None,
        url=None,
        playing=False,
        loop=False,
        controls=False,
        volume=None,
        muted=False,
        playbackRate=1,
        width='100%',
        height='100%',
        style=None,
        playsinline=False,
        currentTime=None,
        secondsLoaded=None,
        duration=None,
        intervalCurrentTime=100,
        intervalSecondsLoaded=500,
        intervalDuration=500,
        seekTo=None,
        **kwargs
    ):
        super().__init__(
            id=id,
            className=className,
            url=url,
            playing=playing,
            loop=loop,
            controls=controls,
            volume=volume,
            muted=muted,
            playbackRate=playbackRate,
            width=width,
            height=height,
            style=style,
            playsinline=playsinline,
            currentTime=currentTime,
            secondsLoaded=secondsLoaded,
            duration=duration,
            intervalCurrentTime=intervalCurrentTime,
            intervalSecondsLoaded=intervalSecondsLoaded,
            intervalDuration=intervalDuration,
            seekTo=seekTo,
            **kwargs
        )
        if url:
            video = VideoFileClip(url)
           
        else:
            self.duration = None
            
            
    def update_video_time(self, clickData,video_duration):
            if clickData and clickData['points']:
                x_click = clickData['points'][0]['x']
                video_time = min(x_click, video_duration or 0)
                return video_time
            else:
                ctx = dash.callback_context
                if ctx.triggered:
                    prop_id = ctx.triggered[0]['prop_id'].split('.')[0]
                    if prop_id == self.id:
                        return dash.no_update
                return 0.0

        

        
        
