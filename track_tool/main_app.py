from flask import Flask, request, jsonify, render_template
import os
import cv2
import os
from flask import Flask, render_template_string, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
import threading
from flask import current_app
from flask import Flask, render_template, request, redirect, url_for, flash
from track_project import TrackProject
from datetime import datetime  
import shutil
from flask import Response, jsonify
import time 
import mask_video
from flask import Flask, send_from_directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECTS_FOLDER = os.path.join(BASE_DIR, 'static', 'projects') 
os.makedirs(PROJECTS_FOLDER, exist_ok=True)
track_project = TrackProject()
NAME_FOLDER=""



app = Flask(__name__)

# Caminho onde a imagem será salva


# Aceitar tipos de imagem (extensões permitidas)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Função para verificar a extensão permitida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Rota para renderizar o template index.html
@app.route('/')
def index():
    # Listar projetos já criados
    projects = [name for name in os.listdir(PROJECTS_FOLDER) if os.path.isdir(os.path.join(PROJECTS_FOLDER, name))]
    return render_template('index.html', projects=projects)

@app.route('/new_project', methods=['GET', 'POST'])
def new_project():
    if request.method == 'POST':
        project_name = request.form.get('project_name')
        video_file = request.files.get('video_file')

        if not project_name:
            flash('Por favor, insira um nome para o projeto.', 'error')
            return redirect(url_for('new_project'))
        
        if not video_file:
            flash('Por favor, faça upload de um vídeo.', 'error')
            return redirect(url_for('new_project'))

        # Criar a pasta do projeto
        project_folder = os.path.join(PROJECTS_FOLDER, secure_filename(project_name))
        os.makedirs(project_folder, exist_ok=True)

        # Salvar o vídeo na pasta do projeto
        video_path = os.path.join(project_folder, secure_filename("video.mp4"))
        video_file.save(video_path)
        #track_project.set_video_path(video_path)

        flash('Projeto criado e vídeo carregado com sucesso!', 'success')
        return redirect(url_for('index'))

    return render_template('new_project.html')

@app.route('/download_video')
def download_video():
    # Caminho para o diretório onde os vídeos estão armazenados
    
    
    print(f'{PROJECTS_FOLDER}/{NAME_FOLDER}','video_m.mp4')

    # Retorna o arquivo de vídeo para o cliente
    return send_from_directory(f'{PROJECTS_FOLDER}/{NAME_FOLDER}','video_m.mp4')


@app.route('/delete_project/<project_name>', methods=['POST'])
def delete_project(project_name):
    # Lógica para deletar o projeto, ex: remover o diretório ou arquivo
    project_path = os.path.join('static', 'projects', project_name)
    if os.path.exists(project_path):
        # Apagar o projeto
        shutil.rmtree(project_path)
    return f"Projeto '{project_name}' deletado com sucesso!", 200



@app.route('/track/<project_name>')
def track(project_name):
    # Substitua 'nome_do_video.mp4' pelo nome real do arquivo de vídeo ou recupere dinamicamente de uma base de dados ou estrutura de arquivos.
    video_filename = "video.mp4"  # Substitua pelo nome do vídeo específico do projeto
    video_path = f"projects/{project_name}/{video_filename}"
    track_project.set_project_name(project_name)
    global NAME_FOLDER
    NAME_FOLDER=project_name

    # Renderiza o template passando o caminho do vídeo
    return render_template('track.html', project_name=project_name, video_path=video_path)




# Rota para salvar a imagem
@app.route('/save-image', methods=['POST'])
def save_image():
    track_project.status="crop image"
    SAVE_FOLDER_OBJECT = f'{PROJECTS_FOLDER}/{NAME_FOLDER}/objects'
    SAVE_FOLDER_TEMPLATE= f'{PROJECTS_FOLDER}/{NAME_FOLDER}'
    if not os.path.exists(SAVE_FOLDER_OBJECT):
        os.makedirs(SAVE_FOLDER_OBJECT)
    # Verifica se um arquivo foi enviado
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'Nenhum arquivo enviado'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Nenhum arquivo selecionado'})

    # Verifica se a extensão do arquivo é permitida
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'message': 'Arquivo inválido. Somente imagens são permitidas.'})
    
    
    
    # Salva o arquivo no diretório 'objects'
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Não deve causar erro agora
    file_path_o = os.path.join(SAVE_FOLDER_OBJECT, f'object_data_{timestamp}.jpg')
    file.save(file_path_o)    
    track_project.set_bounding_box(request.form.get('bounding_box'))
    track_project.set_template(file_path_o)
    #file_path = os.path.join(SAVE_FOLDER_TEMPLATE, 'template.jpg')
    #file_copy.save(file_path)
    

    return jsonify({'success': True, 'message': 'Imagem salva com sucesso!'})

@app.route('/save-video', methods=['POST'])
def save_video():
    # Verifica se o vídeo foi enviado
    if 'video' not in request.files:
        return jsonify({'success': False, 'message': 'Nenhum arquivo de vídeo enviado'})

    video = request.files['video']
    if video.filename == '':
        return jsonify({'success': False, 'message': 'Nenhum vídeo selecionado'})
    # Salva o arquivo de vídeo no diretório 'objects'
    SAVE_FOLDER_TEMPLATE= f'{PROJECTS_FOLDER}/{NAME_FOLDER}'
    video_path = os.path.join(SAVE_FOLDER_TEMPLATE, 'template_video.mp4')
    video.save(video_path)

    return jsonify({'success': True, 'message': 'Vídeo salvo com sucesso!'})







@app.route('/stop-tracking', methods=['POST'])
def stop_tracking():
    # Chama o método stop_tracking da instância track_project
    return  jsonify(track_project.stop_tracking())


@app.route('/mask-objects', methods=['POST'])
def mask_objects():
    out_v=f'{PROJECTS_FOLDER}/{NAME_FOLDER}/video_m.mp4'
    mask_video1=mask_video.hide_objects(track_project.video_path,out_v,track_project.tracking_data['frames'])
    print("mask ok")
    # Chama o método stop_tracking da instância track_project
    return  jsonify( {'state_progress': 'end_mask', 'message': 'fim do maskaramento'})

tracking_progress = []
rectangles = {}

    # Variáveis de controle de rastreamento
tracking_active = False


@app.route('/video_feed')
def video_feed():
    track_project.status="video_feed"

    timestamp = float(request.args.get('timestamp', 0))
    
    select_all = request.args.get('select_all', 'false') == 'true'
    print("rrr",select_all)
    #cap = cv2.VideoCapture('your_video_path.mp4')
    #cap.set(cv2.CAP_PROP_POS_MSEC, timestamp * 7000)
    resp=track_project.start_tracking(timestamp,select_all)
    print(resp)

    resp=Response(resp, mimetype='multipart/x-mixed-replace; boundary=frame')
    return resp

@app.route('/status_endpoint')
def tracking_status():
        return jsonify({'message':track_project.status})


if __name__ == '__main__':
    app.secret_key = 'your_secret_key'  # Para mensagens flash
    app.run(debug=True,port=5056)
