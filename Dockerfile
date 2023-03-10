FROM python:3.9
ADD requirements.txt .
RUN pip install -r requirements.txt
ADD GoBridge.py .
ADD config.ini .
ADD service_secret.json .
EXPOSE 2500
CMD [ "python", "./GoBridge.py" ]
