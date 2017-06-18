from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin

app = Flask(__name__)
app.config.from_pyfile('config.cfg')
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////db/flaskapp.db'
CORS(app)

db = SQLAlchemy(app)
