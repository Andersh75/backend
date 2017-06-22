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
import datetime, calendar
from functions import createtables, allcourses, create_course_date_connection, create_room_class_connection, create_room_date_connection, create_or_fetch_classobj, create_or_fetch_courseobj, create_or_fetch_dateobj, create_or_fetch_roomobj, create_or_fetch_teacherobj, fetch_courseobj




def fetchinglistofslotspercourse(course, starttime, endtime):

    tempdict = {}
    templist = []
    tempdict['code'] = course
    tempdict['slots'] = templist

    print course
    print starttime
    print endtime

    try:
        j = urllib2.urlopen('http://www.kth.se/api/schema/v2/course/%s?startTime=%s&endTime=%s' % (course, starttime, endtime))

        j_obj = json.load(j)

        templist = j_obj['entries']

        tempdict['slots'] = templist

    except Exception, e:
        varcode = "no json for course"
        print varcode
        print course
        print starttime
        print endtime

    return tempdict


def courseyear_from_classdate(code, year, date):

        courseendyearsubq = db.session.query(Courses).filter(and_(Courses.code == code, Courses.endyear == year))
        endyearexists = db.session.query(courseendyearsubq.exists()).scalar()

        coursestartyearsubq = db.session.query(Courses).filter(and_(Courses.code == code, Courses.startyear == year))
        startyearexists = db.session.query(coursestartyearsubq.exists()).scalar()




        if startyearexists:
            startyearobj = db.session.query(Courses).filter(and_(Courses.code == code, Courses.startyear == year)).first()
            startdate = startyearobj.startdate
            enddate = startyearobj.enddate

            print startdate

            print datetime.datetime.strptime(date, "%Y-%m-%d")
            if startdate > datetime.datetime.strptime(date, "%Y-%m-%d"):
                year = year - 1
        else:
            year = year - 1

        return year


def parselistofslotspercourse(tempdict):
    code = tempdict['code']

    for item in tempdict['slots']:
        info = item['info']
        start = item['start']
        end = item['end']
        title = item['title']
        kind_name = item['type_name']
        kind = item['type']
        locations = item['locations']

        date = start[:10]
        starttime = start[11:13]
        endtime = end[11:13]
        year = int(start[:4])
        kind_name = kind_name['sv']


        year = courseyear_from_classdate(code, year, date)

        # print start, "STARTYEAR", year



        # year = pass_courseyear_from_classdate(date)

        courseobj = fetch_courseobj(code, year)
        # print "x"
        dateobj = create_or_fetch_dateobj(datetime.datetime.strptime(date, "%Y-%m-%d"))
        # print "y"
        create_course_date_connection(courseobj, dateobj)
        # print "z"

        for location in locations:
            roomvar = location['name']
            roomlinkvar = None

            try:
                roomlinkvar = location['url']
            except Exception, e:
                varcode = "no url"

            roomobj = create_or_fetch_roomobj(roomvar, roomlinkvar)
            create_room_date_connection(roomobj, dateobj)
            classobj = create_or_fetch_classobj(starttime, endtime, courseobj, dateobj)
            create_room_class_connection(roomobj, classobj)
            if classobj:
                classobj.contentapi = info
                # print "INFO ADDED TO CLASS"
                db.session.commit()

    return "DONE"
