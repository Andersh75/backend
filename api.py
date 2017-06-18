from flask.ext.restless import APIManager
from app import app, db

manager = APIManager(app, flask_sqlalchemy_db=db)
