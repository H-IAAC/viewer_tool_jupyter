import cv2
import ffmpegcv
import os
import time

def hide_objects(video_in, video_out, points=[]):
    print("init mask")
    dir_log = os.path.dirname(os.path.abspath(video_out))
    start_time = time.time()
    cap = cv2.VideoCapture(video_in)

    video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_fps = cap.get(cv2.CAP_PROP_FPS)

    # Reduz as dimensões do vídeo se necessário
    if video_width >= 540 or video_width >= 960:
        video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) / 2)
        video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) / 2)

    out = ffmpegcv.VideoWriter(video_out, 'h264', video_fps)

    # Itera sobre os frames do vídeo
    frame_id = 0  # Contador de frames
    while True:
        ret, img = cap.read()
        if not ret:
            break
        
        # Verifica se o frame_id está na lista de pontos
        for point in points:
            timest=cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
            
            if point['timestamp'] == timest and point['success']==1:
                # Desenha o retângulo no frame com as coordenadas do ponto
                x, y, w, h = point['points']['x'], point['points']['y'], point['points']['w'], point['points']['h']
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), -1)  # Cor verde e espessura 2
                print(point,timest)
                

        # Escreve o frame modificado no arquivo de saída
        out.write(img)
        
        frame_id += 1  # Incrementa o contador de frames

    cap.release()
    out.release()


