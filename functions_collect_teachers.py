from app import db
import urllib
import urllib2
from urllib2 import urlopen
from bs4 import BeautifulSoup
from xml.etree import ElementTree as ET
from models import *
from sqlalchemy.sql import and_, or_, not_
import json
from flask import json
import simplejson
from flask import jsonify

from functions import createtables, allcourses, create_course_date_connection, create_room_class_connection, create_room_date_connection, create_or_fetch_classobj, create_or_fetch_courseobj, create_or_fetch_dateobj, create_or_fetch_roomobj, create_or_fetch_teacherobj, fetch_courseobj






# ADDING TEACHERS TO LIST
# Firstname, Lastname, Email, Username, Department
def staffperdepartment(department):
    try:
        req = urllib2.urlopen('https://www.kth.se/directory/a/%s' % (department))

        xml = BeautifulSoup(req)

        templist = xml.find("table")
        templist = templist.find("tbody")
        templist = templist.findAll("tr")

        templist2 = []
        tempdict = {}

        tempdict2 = {}

        for tr in templist:
            tdlist = tr.findAll("a")
            firstname = tdlist[2].text
            lastname = tdlist[1].text
            email = tdlist[3].text
            username = tdlist[1]['href'][27:]

            tempdict = {'firstname': firstname, 'lastname': lastname, 'email': email, 'username': username}
            templist2.append(tempdict)
            print "ADDED", tempdict['firstname'].upper(), tempdict['lastname'].upper(), "TO LIST OF TEACHERS"

        tempdict2 = {'department': department, 'teacher': templist2}

    except Exception, e:
        varcode = "no list of staff per department"
        print varcode.upper()
        # print x
        # print y

    return tempdict2


# ADDING TEACHERS TO DB IF EMAIL EXSISTS
# Firstname, Lastname, Email, Username, Department
def teachersfromdepartment(templist):
    for items in templist:

        department = items['department']

        for item in items['teacher']:
            firstname = item['firstname']
            lastname = item['lastname']
            email = item['email']
            username = item['username']

            if email:
                teacherobj = create_or_fetch_teacherobj(email)

                teacherobj.firstname = firstname
                teacherobj.lastname = lastname
                teacherobj.email = email
                teacherobj.username = username
                teacherobj.department = department

                db.session.commit()

        print "DONE"
