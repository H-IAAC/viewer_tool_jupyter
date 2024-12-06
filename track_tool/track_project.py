import os
from flask import current_app
import time
import cv2
tracking_progress = []
rectangles = {}

from ultralytics import YOLO

model = YOLO("yolo11n.pt")
    # Variáveis de controle de rastreamento
tracking_active = False
class TrackProject:
    def __init__(self):
        self.tracking_in_progress = False
        self.tracking_thread = None
        self.project_name=""
        self.template_path=''
        self.video_path=''
        self.tracked_points = []
        self.tracking_in_progress = False
        self.tracking_thread = None
        self.status=""
        self.timestamp=0
        self.cord =(15.15, 20.67, 213.45, 213.45)

    def set_project_name(self,name):
        self.project_name=name
        self.video_path = f"static/projects/{self.project_name}/video.mp4"

    def set_template(self,file_path_o):
        self.init_traking_data()
        self.template_path=file_path_o
    
    def set_bounding_box(self,bounding_box):       
        self.cord=tuple(map(float, bounding_box.split(',')))
        print(self.cord)


    def set_video_path(self,video_path):
        print(video_path)
        self.video_path=video_path


    def start_tracking(self,start_time,select_all):
            # Verifica se o rastreamento já está em andamento
            if self.tracking_in_progress==True:
                print("in progress")
                self.status = "in progress"

            # Inicia o rastreamento em um novo thread
            self.tracking_in_progress = True
            #result=self.generate_frames(start_time)
            result=self.track_yolo(start_time)

            return result

    def stop_tracking(self):
        print("stop")
        # Verifica se o rastreamento está em andamento
        self.status = "stop"
        if not self.tracking_in_progress:
            self.status = "stop"
        self.tracking_in_progress = False  
        return {'success': True, 'message': 'Vídeo salvo com sucesso!'}  

    def get_data(self):
        return self.data
    
    def init_traking_data(self):
        self.tracking_data = {
            "start_time": time.time(),
            "frames": []
        }

    
    
    def track_yolo(self, start_time):
        print("Starting face tracking...")

        # Carregar o template e vídeo
        template = cv2.imread(self.template_path, cv2.IMREAD_COLOR)
        cap = cv2.VideoCapture(self.video_path)
        cap.set(cv2.CAP_PROP_POS_MSEC, start_time * 1000)

        # Verificar se o vídeo e o template foram carregados corretamente
        if not cap.isOpened() or template is None:
            print("Error: Could not open video or load template.")
            return {'state_progress': 'error', 'message': 'Video or template failed to load'}

        # Criar o tracker CSRT
        tracker = cv2.legacy.TrackerCSRT_create()
        tracker_initialized = False

               

        bbox = self.cord  # Calcular a largura e altura do bounding box

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret or frame is None:
                print("Fim do vídeo ou erro ao carregar frame.")
                break

            # Inicializar o tracker com o bounding box no primeiro frame
            if not tracker_initialized:
                print(f"Inicializando tracker com bbox: {bbox} e frame shape: {frame.shape}")
                tracker.init(frame, bbox)
                tracker_initialized = True
                print("initttttttttt")

            # Atualizar o tracker com o novo frame
            success, bbox = tracker.update(frame)

            if success:
                # Desenhar a caixa rastreada no frame
                p1 = (int(bbox[0]), int(bbox[1]))
                p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
                cv2.rectangle(frame, p1, p2, (0, 0, 0), -1)
            else:
                print("falha no rastreamento")
                # Se o rastreamento falhar, exibir uma mensagem
                cv2.putText(frame, "Falha no rastreamento", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            # Exibir o frame com a caixa de rastreamento
            #cv2.imshow('Tracking', frame)
            _, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

            # Interromper o processo caso a tecla 'q' seja pressionada
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


        # Liberação de recursos
        cap.release()
        cv2.destroyAllWindows()

        print("Tracking concluído.")
        return {'state_progress': 'completed', 'message': 'Tracking completed successfully'}



    def generate_frames(self,start_time):
  
        global tracking_progress, rectangles
        template = cv2.imread(self.template_path, cv2.IMREAD_COLOR)
        print(self.template_path, '  ',self.video_path)
        cap = cv2.VideoCapture(self.video_path)
        cap.set(cv2.CAP_PROP_POS_MSEC, start_time * 1000)

        tracker = cv2.TrackerKCF_create()
        face_detected = False

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_duration = 1 / cap.get(cv2.CAP_PROP_FPS)  # Duração de cada frame em segundos

        current_time = 0  # Progresso atual em segundos
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            success_frame = False
            rect_to_draw = None

            if not face_detected:
                result = cv2.matchTemplate(gray_frame, cv2.cvtColor(template, cv2.COLOR_BGR2GRAY), cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(result)

                if max_val >= 0.5:
                    x, y = max_loc
                    w, h = template.shape[1], template.shape[0]
                    #tracker.init(frame, (x, y, w, h))
                    face_detected = True
            else:
                success, bbox = tracker.update(frame)
                if success:
                    x, y, w, h = [int(v) for v in bbox]
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Retângulo verde se sucesso
                    success_frame = True
                    rect_to_draw = {"x": x, "y": y, "w": w, "h": h}
                else:
                    # Quando o rastreamento falha, desenha o retângulo em vermelho
                    x, y, w, h = 0, 0, 0, 0  # Definindo um retângulo "nulo" se falhar
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)  # Retângulo vermelho se falha

            # Atualiza dados de progresso
            tracking_progress.append({"start": current_time / (total_frames * frame_duration),
                                    "duration": frame_duration / (total_frames * frame_duration),
                                    "success": success_frame})
            current_time += frame_duration

            # Armazena o retângulo para o tempo específico
            if rect_to_draw:
                rectangles[int(current_time)] = rect_to_draw

            _, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        
        cap.release()
