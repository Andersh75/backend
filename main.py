from app import app, db
from flask import render_template, request, flash, url_for, redirect, abort, session
from flask.ext.sqlalchemy import get_debug_queries
from sqlalchemy import desc, create_engine, func
from sqlalchemy.orm import scoped_session, sessionmaker, joinedload, aliased
from sqlalchemy.ext.declarative import declarative_base
from passlib.hash import sha256_crypt
# from MySQLdb import escape_string as thwart

from socket import *
from functools import wraps
from decimal import Decimal

import gc

import xmltodict

from sqlalchemy import exists
import csv
from datetime import date, datetime, timedelta
from operator import itemgetter
import string

import cookielib
import mechanize

from flask_restplus import Resource, Api, fields
from wtforms import Form, BooleanField, TextField, PasswordField, validators




from api import manager
from models import *
from views import *


manager.create_api(Classes, allow_patch_many=True, allow_delete_many=True, methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'], results_per_page=2000)
manager.create_api(Notourclasses, allow_patch_many=True, allow_delete_many=True, methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'], results_per_page=2000)
manager.create_api(Courses, allow_patch_many=True, allow_delete_many=True, methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'], results_per_page=200)
manager.create_api(Classtypes, allow_patch_many=True, allow_delete_many=True, methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'], results_per_page=200)
manager.create_api(Teachers, allow_patch_many=True, allow_delete_many=True, methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'], results_per_page=200)
manager.create_api(Rooms, allow_patch_many=True, allow_delete_many=True, methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'], results_per_page=2000)

# 

if __name__ == "__main__":
    # db.create_all()
    app.run(host='0.0.0.0', debug=True)
