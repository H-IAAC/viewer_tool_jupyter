ARG ALPINE_VERSION=3.16

FROM alpine:${ALPINE_VERSION}

EXPOSE 8888
EXPOSE 8050

RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN apk update
RUN apk add py-pip build-base linux-headers gcc python3-dev
RUN apk --update add --no-cache g++
RUN pip3 install --no-cache --upgrade pip setuptools wheel && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi



ENV PYTHONUNBUFFERED=1

ENV SRC_PATH=/usr/src/h-iaac/captureX-jupyter

WORKDIR ${SRC_PATH}

COPY ./ ${SRC_PATH}

RUN pip3 install -r ${SRC_PATH}/requirements.txt



CMD ["jupyter", "lab", "--ip", "0.0.0.0", "--no-browse", "--allow-root"]
