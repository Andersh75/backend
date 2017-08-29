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



# ADDING COURSES TO DB
def coursecodeandroundidperyearandterm(x, y):

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

            year = startterm[:4]

            term = startterm[-1:]



            tempdict = {'coursecode': coursecode, 'year': year, 'term': term, 'periodone': False, 'periodtwo': False, 'periodthree': False, 'periodfour': False, 'roundid': roundid}

            print "ADDED", tempdict['coursecode'].upper(), tempdict['year'].upper(), "TO LIST OF COURSES"

            templist.append(tempdict)

    tempdict2 = {'courseinfo': templist}

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
        roundid = item['roundid']

        try:
            req = urllib2.urlopen('http://www.kth.se/api/kopps/v1/course/%s/round/%s:%s/%s' % (coursecode, year, term, roundid))
            xml = BeautifulSoup(req)
            # print xml

            try:
                courseround = xml.find('courseround')

                endweek = courseround['endweek'][-2:]
                item['endweek'] = endweek

                startweek = courseround['startweek'][-2:]
                item['startweek'] = startweek

                endyear = courseround['endweek'][:4]
                item['endyear'] = endyear

                startyear = courseround['startweek'][:4]
                item['startyear'] = startyear


                d = startyear + "-W" + startweek
                item['startdate'] = datetime.datetime.strptime(d + '-1', "%Y-W%W-%w")
                print "STARTDATE: ",item['startdate']

                d = endyear + "-W" + endweek
                item['enddate'] = datetime.datetime.strptime(d + '-0', "%Y-W%W-%w")

                periodone = False
                periodtwo = False
                periodthree = False
                periodfour = False

                if int(startweek) < 5:
                    periodthree = True

                elif int(startweek) < 14:
                    periodfour = True

                elif int(startweek) < 37:
                    periodone = True

                elif int(startweek) < 49:
                    periodtwo = True


                if int(endweek) < 5:
                    periodtwo = True
                    if periodthree:
                        periodfour = True
                        periodone = True
                    if periodfour:
                        periodone = True

                elif int(endweek) < 14:
                    periodthree = True
                    if periodfour:
                        periodone = True
                        periodtwo = True
                    if periodone:
                        periodtwo = True

                elif int(endweek) < 37:
                    periodfour = True
                    if periodone:
                        periodtwo = True
                        periodthree = True
                    if periodtwo:
                        periodthree = True

                elif int(endweek) < 49:
                    periodone = True
                    if periodtwo:
                        periodthree = True
                        periodfour = True
                    if periodthree:
                        periodfour = True

                '''print "coursecode", coursecode
                print "year", year
                print "term", term
                print "roundid", roundid
                print "period one", periodone
                print "period two", periodtwo
                print "period three", periodthree
                print "period four", periodfour
                print "endweek", endweek
                print "startweek", startweek'''

                item['periodone'] = periodone
                item['periodtwo'] = periodtwo
                item['periodthree'] = periodthree
                item['periodfour'] = periodfour



            except Exception, e:
                item['endweek'] = None
                item['startweek'] = None
                item['endyear'] = None
                item['startyear'] = None
                item['enddate'] = None
                item['startdate'] = None
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
    periodone = item['periodone']
    periodtwo = item['periodtwo']
    periodthree = item['periodthree']
    periodfour = item['periodfour']

    roundid = item['roundid']
    responsible = item['emailcourseresponsible']
    startweek = item['startweek']
    endweek = item['endweek']
    startyear = item['startyear']
    endyear = item['endyear']
    startdate = item['startdate']
    enddate = item['enddate']

    # print code, year, term, periods, roundid, responsible, startweek, endweek

    courseobj = create_or_fetch_courseobj(code, year)
    courseobj.term = term
    courseobj.periodone = periodone
    courseobj.periodtwo = periodtwo
    courseobj.periodthree = periodthree
    courseobj.periodfour = periodfour
    courseobj.roundid = int(roundid)
    courseobj.startweek = int(startweek)
    courseobj.endweek = int(endweek)
    courseobj.startyear = int(startyear)
    courseobj.endyear = int(endyear)
    courseobj.startdate = startdate
    courseobj.enddate = enddate


    # COURSE RESPONSIBLE NOT ADDED TO DB IF NOT IN LIST OF TEACHERS
    if responsible:
        # print "responsible!!!!"
        teachersubq = db.session.query(Teachers).filter(Teachers.email == responsible)
        responsibleexists = db.session.query(teachersubq.exists()).scalar()
        if responsibleexists:
            # print "exists!!!!"
            courseobj.responsible_id = Teachers.query.filter_by(email=responsible).first().id

    print "ADDED TERM, PERIODS, ROUNDID, STARTWEEK, ENDWEEK AND COURSE RESPONSIBLE TO", courseobj.code, courseobj.year

    db.session.commit()

    # print "hej!"






def fetchinglistofcodesfordepartmentcourses(department):

    tempdict = {}

    # print "1"

    try:
        # print "2"
        j = urllib2.urlopen('http://www.kth.se/api/kopps/v2/courses/%s.json' % (department))
        # print "3"
        j_obj = json.load(j)
        # print "4"
        templist = []
        # print "5"
        for item in j_obj['courses']:
            templist.append(item['code'])

        # print "6"

        tempdict = {'department': j_obj['department'], 'courses': templist}

    except Exception, e:
        varcode = "no list of codes for department courses"
        print varcode

    return tempdict



def jsonifycoursesfromdepartmentold(tempdict):

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


def jsonifycoursesfromdepartment(tempdict):

    templist2 = []
    tempdict2 = {}

    for item in tempdict['courses']:

        try:
            j = urllib2.urlopen('http://www.kth.se/api/kopps/v2/course/%s' % (item))
            # print "3"
            jload = json.load(j)

            # print jload['title']['en']

            req = urllib2.urlopen('http://www.kth.se/api/kopps/v1/course/%s' % (item))

            xml = BeautifulSoup(req)

            # varname = xml.title.string
            try:
                varcode = jload['code']
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
                varname = jload['title']['en']
                # print varname.encode('utf-8')
                # print varname

            except Exception, e:
                varname = None
                # print varname

            tempdict2 = {'code': varcode, 'name': varname, 'examiner': varmail, 'department': tempdict['department']}

            # print tempdict2
            # print "sss"
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

            if existscourse:
                latestcourse = latestcoursesubq.first()
                latestcourse.name = name
                db.session.commit()

            if existscourse and teacherobj:
                latestcourse = latestcoursesubq.first()
                # latestcourse.name = name
                latestcourse.examiner_id = teacherobj.id
                db.session.commit()
            else:
                print "COURSE OR EXAMINER NOT EXISTING"
                print code
                print examiner
