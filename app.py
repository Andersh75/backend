from flask import Flask,jsonify
import requests
import simplejson
import json
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin


app = Flask(__name__)
app.config['SQALCHEMY_DATABASE_URI'] = 'sqlite://///db/flaskapp.db'
CORS(app)

db = SQLAlchemy(app)

class ExampleTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)

db.create_all()


@app.route("/")
def hello():
    uri = "https://mdn.github.io/learning-area/javascript/oojs/json/superheroes.json"
    try:
        uResponse = requests.get(uri)
    except requests.ConnectionError:
       return "Connection Errsssss"
    Jresponse = uResponse.text
    # return "Hello World!"
    return Jresponse


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
