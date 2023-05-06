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
WORKDIR /Amy
COPY . /Amy

ENV DISPLAY=:0
RUN Xvfb :0 -screen 0 1024x768x16 &

# Creates a non-root user with an explicit UID and adds permission to access the \\app folder
# For more info, please refer to https:\\\\aka.ms\\vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" amy && chown -R amy .
USER amy

CMD ["sh", "-c", "export DISPLAY=:0" && "python", "-c", "import", "pyaudio" && "gunicorn", "--bind", "0.0.0.0:1750", "run.py"]
