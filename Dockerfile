FROM alpine:latest

# Copy Files To Container
COPY main.py /demodownloader/main.py
COPY requirements.txt /demodownloader/

# Set working directory
WORKDIR /demodownloader

# Make empty files/folders required
RUN mkdir /downloadeddemos
RUN mkdir /config
RUN touch /config/saved_codes.txt

# Update conatiner | Probably dont need to do this but it cant hurt things so ¯\_(ツ)_/¯
RUN apk update
RUN apk upgrade --no-cache

# Install Python and Pip
ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

# Install requirements
RUN pip3 install -r requirements.txt

# env variables
ENV APIKEY=
ENV STEAMID=
ENV STEAMIDKEY=
ENV KNOWNSHARECODE=
ENV USERNAME=
ENV PASSWORD=
ENV WAITTIME=60
ENV FINISHEDWAITTIME=1200
ENV ENABLEDEBUGGING=False

# Run my *super cool program*
CMD [ "python3" , "main.py" ]

# Uncomment this and comment the one above if you want to peek into the container without it doing stuff.
# Theres probably a proper way to do this but i dont know it and this works so ¯\_(ツ)_/¯
#CMD [ "ping" , "127.0.0.1" ]