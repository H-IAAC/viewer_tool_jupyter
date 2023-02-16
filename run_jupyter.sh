DOCKERCMD=nvidia-docker
PORT=9999
IMAGE=hiaac4-full:latest
WORKDIR=$(realpath $(pwd))
$DOCKERCMD run  -it --rm  -e HOME=$WORKDIR -e SHELL="/bin/bash" -p $PORT:$PORT -w $WORKDIR -v$WORKDIR:$WORKDIR --ipc=host $IMAGE python -m jupyterlab --allow-root --port $PORT --no-browser --ip='0.0.0.0' --NotebookApp.token='' --NotebookApp.password=''
