# For more information, please refer to https:\\\\aka.ms\\vscode-docker-python
FROM python:3.10-slim

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt .

RUN apt-get update && apt-get install ffmpeg libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0 xvfb python3-pip xauth python3-tk python3-dev -y 
RUN python -m pip install pyaudio==0.2.11
RUN python -m pip install --upgrade pip
RUN python -m  pip install --upgrade setuptools
RUN python -m pip install -r requirements.txt



WORKDIR /emma
COPY . /emma
ENV FLASK_APP emma/web_server/app.py
ENV FLASK_ENV development
EXPOSE 3018

RUN echo '#!/bin/bash' > /emma/startup.sh && \
	echo 'Xvfb :99 -screen 0 1280x1024x16 &' >> /emma/startup.sh && \
	echo 'export DISPLAY=:99' >> /emma/startup.sh && \
	echo 'python -c "import pyaudio"' >> /emma/startup.sh && \
	echo 'python run.py' >> /emma/startup.sh && \
	chmod +x /emma/startup.sh

# Start Xvfb and run the application using the shell script
CMD ["/emma/startup.sh"]
