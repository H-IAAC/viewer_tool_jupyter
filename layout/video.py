import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import dash_player


from dash import dcc, html
import dash_player

class VideoPlayer(html.Div):
    
    def __init__(self, id_upload, id_output, *args, **kwargs):
        super().__init__([
            # Upload de vídeo
            dcc.Upload(
                id=id_upload,
                children=html.Div([
                    'Arraste e solte ou selecione um vídeo',
                    html.A('')
                ]),
                style={
                    'borderWidth': '1px',
                    'borderStyle': 'dashed'
                },
                accept='video/*'
            ),

            # Player de vídeo e mensagem de "sem vídeo"
            html.Div(id=id_output, children=[
                dash_player.DashPlayer(
                    id='video-player',
                    controls=True,
                    width='100%',
                    style={'display': 'none'}  # Esconder o player inicialmente
                ),
                html.Div(id='no-video-message', children="Por favor, faça o upload de um vídeo.")
            ]),

            # Container para o seletor de zoom e o botão de etiquetar, alinhados na horizontal
            html.Div(id='controls-container', children=[
                # Select booleano para ativar/desativar o zoom
                html.Div(id='zoom-container', children=[
                    dcc.Checklist(
                        id='zoom-loop',
                        options=[{'label': 'Zoom Loop', 'value': 'zoom'}],
                        value=[],  # Inicialmente desativado
                        inline=True,
                        style={'margin': '10px'}
                    )
                ], style={'display': 'none'}),  # Esconder inicialmente

                # Botão para etiquetar vídeo
                html.Div(id='etiquetar-container', children=[
                    html.Button('Etiquetar Vídeo', id='btn-etiquetar-video', n_clicks=0, style={'margin-left': '10px'})
                ], style={'display': 'none'})  # Esconder inicialmente
            ], style={
                'display': 'flex',
                'flexDirection': 'row',
                'alignItems': 'center',
                'margin-top': '10px',
            })
        ], *args, **kwargs)

        self.id_upload = id_upload
        self.id_output = id_output

    def register_callbacks(self, app):
        @app.callback(
            [Output(self.id_output, 'children'),
             Output('zoom-container', 'style'),
             Output('etiquetar-container', 'style')],
            Input(self.id_upload, 'contents'),
            State(self.id_upload, 'filename')
        )
        def update_video(contents, filename):
            if contents is not None:
                # Mostrar os controles de zoom e o botão quando o vídeo for carregado
                zoom_style = {'display': 'block'}
                etiquetar_style = {'display': 'block'}
                
                return (
                    dash_player.DashPlayer(
                        id='video-player',
                        url=contents,
                        controls=True,
                        width='100%',
                    ),
                    zoom_style,  # Mostrar o seletor de zoom
                    etiquetar_style  # Mostrar o botão "Etiquetar Vídeo"
                )
            # Caso nenhum vídeo tenha sido carregado, esconder os controles
            return (
                "Por favor, faça o upload de um vídeo.",
                {'display': 'none'},  # Esconder o seletor de zoom
                {'display': 'none'}  # Esconder o botão "Etiquetar Vídeo"
            )



# Callback separado para controlar o loop de zoom entre 30 e 100 segundos
        @app.callback(
            Output('video-player', 'seekTo'),
            [Input('zoom-loop', 'value'),
             Input('video-player', 'currentTime'),
             Input('stored_timestamp', 'data')
             ],
            [State('video-player', 'duration'),State('line-plot_zoom', 'figure')]
        )
        def control_zoom_loop(zoom_value, current_time, stored_time,video_duration,figure):
            if stored_time:
                if stored_time['type'] != 'video_player':
                    return stored_time['timestamp']

                if 'zoom' in zoom_value:
                    xaxis_range = figure['layout']['xaxis'].get('range', None)
                    if xaxis_range is not None:
                        x_min, x_max = xaxis_range
                    # Verifica se o tempo atual está fora do intervalo de 30 a 100 segundos
                    if current_time >= x_max:
                        return x_min  # Reiniciar no segundo 30 se passar do 100
                    elif current_time < x_min:
                        return dash.no_update  # Não faz nada se estiver antes de 30 segundos
            
            return dash.no_update  # Se o loop não estiver ativado, deixa o vídeo rodar normalmente
