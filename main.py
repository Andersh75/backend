from flask import render_template, request, flash, url_for, redirect, abort, session
from flask.ext.sqlalchemy import get_debug_queries
from sqlalchemy import desc, create_engine, func
from sqlalchemy.orm import scoped_session, sessionmaker, joinedload, aliased
from sqlalchemy.ext.declarative import declarative_base
from passlib.hash import sha256_crypt
# from MySQLdb import escape_string as thwart
from xml.etree import ElementTree as ET
from socket import *
from functools import wraps
from decimal import Decimal
from bs4 import BeautifulSoup
import gc
import urllib
import urllib2
from urllib2 import urlopen
import xmltodict
import json
from flask import json
from sqlalchemy import exists
import csv
from datetime import date, datetime, timedelta
from operator import itemgetter
import string
from sqlalchemy.sql import and_, or_, not_
import cookielib
import mechanize
import simplejson
from flask import jsonify
from flask_restplus import Resource, Api, fields
from wtforms import Form, BooleanField, TextField, PasswordField, validators


from app import app, db

from api import manager
from models import *
from views import *



manager.create_api(Person)
manager.create_api(Pet)



if __name__ == "__main__":
    db.create_all()
    app.run(host='0.0.0.0', debug=True)