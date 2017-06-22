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
import cookielib
import mechanize


def open_password_protected_site(link):

    # Browser
    br = mechanize.Browser()

    # Enable cookie support for urllib2
    cookiejar = cookielib.LWPCookieJar()
    br.set_cookiejar(cookiejar)

    # Broser options
    br.set_handle_equiv(True)
    br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)

    # ??
    # br.set_handle_refresh( mechanize._http.HTTPRefreshProcessor(), max_time = 1 )

    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
    # print "heh"
    # authenticate
    br.open(link)

    br.select_form(nr=0)
    # these two come from the code you posted
    # where you would normally put in your username and password
    br["username"] = 'ahell'
    br["password"] = '-Gre75kger-'
    res = br.submit()

    print "Success!\n"

    return br


# CREATE TABLES
def createtables():
    db.create_all()
    db.session.commit()


def allcourses():
    templist = db.session.query(Courses).order_by(Courses.code.desc()).all()
    # templist = db.session.query(Courses).order_by(Courses.code).all()
    return templist


def create_course_date_connection(courseobj, dateobj):

    if courseobj and dateobj:
        coursedatesubq = db.session.query(Dates).join(Dates.courses).filter(and_(Dates.id == dateobj.id, Courses.id == courseobj.id))
        alreadycoursedate = db.session.query(coursedatesubq.exists()).scalar()

        if alreadycoursedate:
            print "COURSE-DATE EXISTS ALREADY"
        else:
            print "NO PREVIOUS COURSE-DATE"
            print "CREATING COURSE-DATE"
            dateobj.courses.append(courseobj)
            db.session.commit()
    else:
        print "NO COURSOBJ OR DATEOBJ"


def create_room_class_connection(roomobj, classobj):

    if roomobj and classobj:
        roomclasssubq = db.session.query(Classes).join(Classes.rooms).filter(and_(Classes.id == classobj.id, Rooms.id == roomobj.id))
        alreadyroomclass = db.session.query(roomclasssubq.exists()).scalar()

        if alreadyroomclass:
            print "ROOM-CLASS EXISTS ALREADY"
        else:
            print "NO PREVIOUS ROOM-CLASS"
            print "CREATING ROOM-CLASS"
            classobj.rooms.append(roomobj)
            db.session.commit()
    else:
        print "NO ROOMOBJ OR CLASSOBJ"


def create_room_date_connection(roomobj, dateobj):

    if roomobj and dateobj:
        roomdatesubq = db.session.query(Dates).join(Dates.rooms).filter(and_(Dates.id == dateobj.id, Rooms.id == roomobj.id))
        alreadyroomdate = db.session.query(roomdatesubq.exists()).scalar()

        if alreadyroomdate:
            print "ROOM-DATE EXISTS ALREADY"
        else:
            print "NO PREVIOUS ROOM-DATE"
            print "CREATING ROOM-DATE"
            dateobj.rooms.append(roomobj)
            db.session.commit()
    else:
        print "NO ROOMOBJ OR DATEOBJ"


def create_or_fetch_classobj(starttimevar, endtimevar, courseobj, dateobj):

    classobj = None

    if starttimevar and endtimevar and courseobj and dateobj:
        #print int(starttimevar)
        #print endtimevar
        #print courseobj.id
        #print dateobj.id
        classsubq = db.session.query(Classes).join(Classes.courses).join(Classes.rooms).join(Classes.dates).filter(and_(Courses.id == courseobj.id, Dates.id == dateobj.id, Classes.starttime == starttimevar, Classes.endtime == endtimevar))
        alreadyclass = db.session.query(classsubq.exists()).scalar()

        #test = db.session.query(Classes).join(Classes.courses).join(Classes.rooms).join(Classes.dates).filter(and_(Courses.id == 70, Dates.id == 306, Classes.starttime == 8, Classes.endtime == 10)).first()
        # print test

        if alreadyclass:
            print "CLASSOBJECT FETCHED"
            classobj = classsubq.first()
        else:
            print "NO PREVIOUS CLASSOBJECT"

            try:
                tempdict = {}
                tempdict['starttime'] = int(starttimevar)
                tempdict['endtime'] = int(endtimevar)
                tempdict['courses_id'] = courseobj.id
                tempdict['dates_id'] = dateobj.id

                record = Classes(**tempdict)
                classobj = record
                db.session.add(record)
                db.session.commit()
                print "CREATED CLASSOBJECT"

            except Exception, e:
                varcode = "UNIQUE CONSTRAINT"
                print varcode
                db.session.rollback()
                # raise


    else:
        print "NO STARTTIMEVAR OR ENDTIMEVAR OR COURSEOBJ OR DATEOBJ"

    return classobj


def create_or_fetch_courseobj(codevar, yearvar):

    courseobj = None

    if codevar and yearvar:

        coursesubq = db.session.query(Courses).filter(and_(Courses.code == codevar, Courses.year == yearvar))
        alreadycourse = db.session.query(coursesubq.exists()).scalar()

        if alreadycourse:

            courseobj = coursesubq.first()
            print "COURSEOBJECT", courseobj.code, courseobj.year, "FETCHED"
        else:
            tempdict = {}
            tempdict['code'] = codevar
            tempdict['year'] = int(yearvar)
            record = Courses(**tempdict)
            courseobj = record
            print "NO PREVIOUS COURSEOBJECT - CREATING COURSEOBJECT", courseobj.code, courseobj.year
            db.session.add(record)
            db.session.commit()
    else:
        print "NO CODEVAR OR YEARVAR"

    return courseobj



def create_or_fetch_dateobj(datevar):

    dateobj = None

    if datevar:
        datesubq = db.session.query(Dates).filter(Dates.date == datevar)
        alreadydate = db.session.query(datesubq.exists()).scalar()

        if alreadydate:
            print "DATEOBJECT FETCHED"
            dateobj = datesubq.first()
        else:
            print "NO PREVIOUS DATEOBJECT"
            print "CREATING DATEOBJECT"
            tempdict = {}
            tempdict['date'] = datevar
            record = Dates(**tempdict)
            dateobj = record
            db.session.add(record)
            db.session.commit()
    else:
        print "NO DATEVAR"

    return dateobj



def create_or_fetch_roomobj(roomvar, linkvar):
    roomobj = None
    # print "HEJ"
    roomvarlist = roomvar.split()
    roomvar = roomvarlist[0]
    # print "HOPP"

    alreadyroomlink = False
    alreadyroom = False

    if linkvar:
        roomlinksubq = db.session.query(Rooms).filter(Rooms.link == linkvar)
        alreadyroomlink = db.session.query(roomlinksubq.exists()).scalar()

    if roomvar:
        roomsubq = db.session.query(Rooms).filter(Rooms.name == roomvar)
        alreadyroom = db.session.query(roomsubq.exists()).scalar()


    if alreadyroomlink:
        if alreadyroom:
            roomobj = roomlinksubq.first()
            print "ROOMOBJECT FETCHED"
        else:
            if roomvar:
                roomobj = roomlinksubq.first()
                roomobj.name = roomvar
                db.session.commit()
                print "ROOMOBJECT FETCHED"
            else:
                roomobj = roomlinksubq.first()

    else:
        if alreadyroom:
            roomobj = roomsubq.first()
            print "ROOMOBJECT FETCHED"
            if linkvar:
                roomobj.link = linkvar
                db.session.commit()
        else:
            tempdict = {}

            if roomvar:
                tempdict['name'] = roomvar

            if linkvar:
                tempdict['link'] = linkvar

            if roomvar or linkvar:
                record = Rooms(**tempdict)
                roomobj = record
                db.session.add(record)
                db.session.commit()
                print "NO PREVIOUS ROOMOBJECT"
                print "CREATING ROOMOBJECT"
            else:
                print "NO ROOMVAR OR LINKVAR"


    return roomobj




def create_or_fetch_teacherobj(emailvar):

    teacherobj = None

    if emailvar:
        teachersubq = db.session.query(Teachers).filter(Teachers.email == emailvar)
        alreadyteacher = db.session.query(teachersubq.exists()).scalar()

        if alreadyteacher:
            teacherobj = teachersubq.first()
            print "TEACHEROBJECT FETCHED", teacherobj.email.upper()
        else:
            tempdict = {}
            tempdict['email'] = emailvar
            record = Teachers(**tempdict)
            teacherobj = record
            print "NO PREVIOUS TEACHEROBJECT - CREATING TEACHEROBJECT", teacherobj.email.upper()
            db.session.add(record)
            db.session.commit()
    else:
        print "NO EMAILVAR"

    return teacherobj


def fetch_courseobj(codevar, yearvar):

    courseobj = None

    if codevar and yearvar:
        coursesubq = db.session.query(Courses).filter(and_(Courses.code == codevar, Courses.year == yearvar))
        alreadycourse = db.session.query(coursesubq.exists()).scalar()

        if alreadycourse:
            print "COURSEOBJECT FETCHED"
            courseobj = coursesubq.first()
        else:
            print "NO COURSEOBJECT TO FETCH"
    else:
        print "NO CODEVAR OR YEARVAR"

    return courseobj
