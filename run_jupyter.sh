export PORT=8888
docker run  -it --rm  -e SHELL="/bin/bash" -e HOME=`pwd` -p ${PORT}:${PORT} -v`pwd`:`pwd` -w`pwd` -u $(id -u ${USER}):$(id -g ${USER}) hiaac4-visualization python -m jupyterlab --port ${PORT} --no-browser --ip='0.0.0.0' --NotebookApp.token='' --NotebookApp.password=''
