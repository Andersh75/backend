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


# CREATE TABLES
def createtables():
    db.create_all()
    db.session.commit()


# ADDING TEACHERS TO DB
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


# ADDING COURSES TO DB
def courseinfoperyearandterm(x, y):

    templist = []
    tempdict2 = {}
    tempdict2['year'] = None
    tempdict2['round'] = None
    tempdict2['courseinfo'] = templist

    # try:
    req = urllib2.urlopen('http://www.kth.se/api/kopps/v1/courseRounds/%s:%s' % (x, y))

    xml = BeautifulSoup(req)

    items = xml.findAll("courseround")

    templist = []

    for item in items:

        coursecode = item['coursecode']
        if coursecode[:2] == "AI":
            startterm = item['startterm']
            roundid = item['roundid']

            period = None

            year = startterm[:4]

            term = startterm[-1:]

            tempdict = {'coursecode': coursecode, 'year': year, 'term': term, 'period': period, 'startterm': startterm, 'roundid': roundid}

            print "ADDED", tempdict['coursecode'].upper(), tempdict['year'].upper(), "TO LIST OF COURSES"

            templist.append(tempdict)

    tempdict2 = {'year': x, 'round': y, 'courseinfo': templist}

    '''
    except Exception, e:
        varcode = "no list of courserounds"
        print varcode
        print x
        print y
    '''
    return tempdict2








def addcoursestotables_first(tempdict):

    for item in tempdict['courseinfo']:
        coursecode = item['coursecode']

        year = item['year']
        term = item['term']
        period = item['period']
        roundid = item['roundid']

        try:
            req = urllib2.urlopen('http://www.kth.se/api/kopps/v1/course/%s/round/%s:%s/%s' % (coursecode, year, term, roundid))
            xml = BeautifulSoup(req)
            # print xml

            try:
                courseround = xml.find('courseround')

                endweek = courseround['endweek']
                item['endweek'] = endweek

                startweek = courseround['startweek']
                item['startweek'] = startweek

            except Exception, e:
                item['endweek'] = None
                item['startweek'] = None
                varcode = "no courseround"
                print varcode

            try:
                courseresponsible = xml.find('courseresponsible')

                emailcourseresponsible = courseresponsible['primaryemail']

                item['emailcourseresponsible'] = emailcourseresponsible

            except Exception, e:
                item['emailcourseresponsible'] = None
                varcode = "no courseresponsible"
                print varcode, "in", coursecode

            coursesfromdepartment2(item)
            # print "XXXXXXXXXX"

        except Exception, e:
            print "NOT FINDING COURSE", coursecode, year
            continue


def coursesfromdepartment2(item):

    code = item['coursecode']
    year = item['year']
    term = item['term']
    period = item['period']
    roundid = item['roundid']
    responsible = item['emailcourseresponsible']
    startweek = item['startweek']
    endweek = item['endweek']

    # print code, year, term, period, roundid, responsible, startweek, endweek

    courseobj = create_or_fetch_courseobj(code, year)
    courseobj.term = term
    courseobj.period = period
    courseobj.roundid = roundid
    courseobj.startweek = startweek
    courseobj.endweek = endweek



    if responsible:
        # print "responsible!!!!"
        teachersubq = db.session.query(Teachers).filter(Teachers.email == responsible)
        responsibleexists = db.session.query(teachersubq.exists()).scalar()
        if responsibleexists:
            # print "exists!!!!"
            courseobj.responsible_id = Teachers.query.filter_by(email=responsible).first().id

    print "ADDED TERM, PERIOD, ROUNDID, STARTWEEK, ENDWEEK AND COURSE RESPONSIBLE TO", courseobj.code, courseobj.year

    db.session.commit()

    # print "hej!"



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
            tempdict['year'] = yearvar
            record = Courses(**tempdict)
            courseobj = record
            print "NO PREVIOUS COURSEOBJECT - CREATING COURSEOBJECT", courseobj.code, courseobj.year
            db.session.add(record)
            db.session.commit()
    else:
        print "NO CODEVAR OR YEARVAR"

    return courseobj


def fetchinglistofcodesfordepartmentcourses(department):

    tempdict = {}

    print "1"

    try:
        print "2"
        j = urllib2.urlopen('http://www.kth.se/api/kopps/v2/courses/%s.json' % (department))
        print "3"
        j_obj = json.load(j)
        print "4"
        templist = []
        print "5"
        for item in j_obj['courses']:
            templist.append(item['code'])

        print "6"

        tempdict = {'department': j_obj['department'], 'courses': templist}

    except Exception, e:
        varcode = "no list of codes for department courses"
        print varcode

    return tempdict





def jsonifycoursesfromdepartment(tempdict):

    templist2 = []
    tempdict2 = {}

    for item in tempdict['courses']:

        try:
            req = urllib2.urlopen('http://www.kth.se/api/kopps/v1/course/%s' % (item))

            xml = BeautifulSoup(req)

            # varname = xml.title.string
            try:
                varcode = xml.course['code']
                # print varcode

            except Exception, e:
                varcode = None
                # print varcode

            try:
                varmail = xml.examiner['primaryemail']
                # print varmail

            except Exception, e:
                varmail = None
                # print varmail

            try:
                varname = xml.title.string
                # print varname.encode('utf-8')
                # print varname

            except Exception, e:
                varname = None
                # print varname

            tempdict2 = {'code': varcode, 'name': varname, 'examiner': varmail, 'department': tempdict['department']}

            templist2.append(tempdict2)

        except Exception, e:
            varcode = "no URL"
            print varcode + " " + item
            continue

    return templist2


def coursesfromdepartment3(templist):
    for items in templist:
        for item in items:
            name = item['name']
            code = item['code']
            examiner = item['examiner']
            department = item['department']

            teacherobj = create_or_fetch_teacherobj(examiner)

            latestcoursesubq = db.session.query(Courses).filter(Courses.code == code).order_by(Courses.year.desc())
            existscourse = db.session.query(latestcoursesubq.exists()).scalar()

            if existscourse and teacherobj:
                latestcourse = latestcoursesubq.first()
                latestcourse.name = name
                latestcourse.examiner_id = teacherobj.id
                db.session.commit()
            else:
                print "COURSE OR EXAMINER NOT EXISTING"
                print code
                print examiner
