from flask import Flask,jsonify
import requests
import simplejson
import json
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin


app = Flask(__name__)
CORS(app)

@app.route("/")
def hello():
    uri = "https://mdn.github.io/learning-area/javascript/oojs/json/superheroes.json"
    try:
        uResponse = requests.get(uri)
    except requests.ConnectionError:
       return "Connection Error"
    Jresponse = uResponse.text
    # return "Hello World!"
    return Jresponse


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
