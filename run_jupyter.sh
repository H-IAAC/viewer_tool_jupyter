WORKDIR=$(realpath $(pwd))
nvidia-docker run -it -p 9999:9999 --ipc=host hiaac-full4:latest jupyter lab --no-browser --ip=0.0.0.0 --port 9999 --allow-root --NotebookApp.token= --notebook-dir='/home/nonroot/'
