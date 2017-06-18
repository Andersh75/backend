FROM python:2.7
ADD . /db
ADD . /flaskapp
WORKDIR /flaskapp
EXPOSE 5000
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "main.py"]
