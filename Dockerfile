FROM python:3.11-slim

RUN adduser gobridge
WORKDIR /home/gobridge
USER gobridge

ADD requirements.txt .
RUN pip install  --user -r requirements.txt
ADD GoBridge.py .
ADD config.ini .

EXPOSE 2500
CMD [ "python","-u", "./GoBridge.py" ]
