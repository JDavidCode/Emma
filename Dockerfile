# For more information, please refer to https:\\\\aka.ms\\vscode-docker-python
FROM python:3.10-slim

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt .

# CV2 Dependencies
RUN apt-get update && apt-get install ffmpeg libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0 xvfb python3-pip xauth libespeak-dev -y 
RUN python -m pip install pyaudio==0.2.11
RUN python -m pip install --upgrade pip
RUN python -m  pip install --upgrade setuptools
RUN python -m pip install -r requirements.txt

WORKDIR /emma
COPY . /emma

ENV FLASK_APP emma/web_server/app.py
ENV FLASK_ENV development
EXPOSE 3018

CMD ["sh", "-c", "python -c 'import pyaudio' && python run.py"]
