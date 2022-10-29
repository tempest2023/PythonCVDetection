# Server
FROM python:3.9.14-buster

ADD ./dockerFile.tgz /

WORKDIR /WebRTCObjectDetection

RUN cd /WebRTCObjectDetection && \
chmod +x startup.sh

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y

RUN pip install pipenv
RUN pipenv install --dev

ENV ROLE server

ENV HOST 0.0.0.0
ENV PORT 8360

EXPOSE 8080 8080

ENTRYPOINT ["nohup", "sh", "/WebRTCObjectDetection/startup.sh", "&"]
