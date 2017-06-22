from app import app, db
import requests
from functions_collect_teachers import staffperdepartment, teachersfromdepartment
from functions_collect_courses import coursesfromdepartment3, jsonifycoursesfromdepartment, fetchinglistofcodesfordepartmentcourses, coursesfromdepartment2, addcoursestotables_first, coursecodeandroundidperyearandterm
from functions import open_password_protected_site, createtables, allcourses, create_course_date_connection, create_room_class_connection, create_room_date_connection, create_or_fetch_classobj, create_or_fetch_courseobj, create_or_fetch_dateobj, create_or_fetch_roomobj, create_or_fetch_teacherobj, fetch_courseobj
from functions_collect_slots import courseyear_from_classdate, fetchinglistofslotspercourse, parselistofslotspercourse
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
from datetime import timedelta




@app.route('/restartall')
def restartall():

    db.drop_all()
    db.session.commit()

    createtables()

    # csvimporter()

    tempdict = {}
    templist = []

    departments = ["AIB", "AIC", "AID", "AIE"]

    # ADD_ALL_TEACHERS_TO_LIST
    for item in departments:

        # Firstname, Lastname, Email, Username
        tempdict = staffperdepartment(item)
        templist.append(tempdict)

    # ADD_ALL_TEACHERS_IN_LIST_TO_DB
    teachersfromdepartment(templist)



    tempdict = {}
    templist = []


    # COLLECTING COURSE CODE AND ROUNDID PER YEAR AND TERM
    tempdict20151 = coursecodeandroundidperyearandterm(2015, 1)
    tempdict20152 = coursecodeandroundidperyearandterm(2015, 2)
    tempdict20161 = coursecodeandroundidperyearandterm(2016, 1)
    tempdict20162 = coursecodeandroundidperyearandterm(2016, 2)
    tempdict20171 = coursecodeandroundidperyearandterm(2017, 1)
    tempdict20172 = coursecodeandroundidperyearandterm(2017, 2)


    # ROUND ID IS LIKE PART ONE OR TWO OF TERM
    # COLLECT STARTWEEK, ENDWEEK, PERIODS AND COURSE RESPONSIBLE
    # ADD COURSE TO DB - NO INFO ON EXAMINER YET
    addcoursestotables_first(tempdict20151)
    addcoursestotables_first(tempdict20152)
    addcoursestotables_first(tempdict20161)
    addcoursestotables_first(tempdict20162)
    addcoursestotables_first(tempdict20171)
    addcoursestotables_first(tempdict20172)


    # COLLECTING EXAMNINER FOR EACH COURSE AND ADDS TO LATEST COURSE IN DB
    for item in departments:
        tempdict = fetchinglistofcodesfordepartmentcourses(item)
        templist.append(jsonifycoursesfromdepartment(tempdict))
    coursesfromdepartment3(templist)


    return "restartall"


# Adding slots from Social for all courses
@app.route('/slotsfromapi')
def slotsfromapi():

    linklist = []

    br = open_password_protected_site("https://login.kth.se/login/")

    # testcourse = ["AI2808"]

    templist = allcourses()
    # templist = testcourse
    for idx, item in enumerate(templist):
        # for idx, item in enumerate(testcourse):
        coursecode = item.code
        year = item.year
        # Fetching slots from schedule API
        print coursecode

        startdate = item.startdate

        print startdate.strftime("%Y-%m-%d")

        enddate = startdate + timedelta(days=365)

        print enddate.strftime("%Y-%m-%d")

        tempdict = {}
        tempdict = fetchinglistofslotspercourse(coursecode, startdate.strftime("%Y-%m-%d"), enddate.strftime("%Y-%m-%d"))
        parselistofslotspercourse(tempdict)



# Adding slots from Social for all courses
@app.route('/slotsfromsocial')
def slotsfromsocial():

    linklist = []

    br = open_password_protected_site("https://login.kth.se/login/")

    # testcourse = db.session.query(Courses).filter(Courses.code == "AI2807")

    templist = allcourses()
    # templist = testcourse
    for idx, item in enumerate(templist):
        # for idx, item in enumerate(testcourse):
        coursecode = item.code
        year = item.year
        # Fetching slots from schedule API
        print coursecode
        tempdict = {}




        #url = br.open('https://www.kth.se/social/course/%s/calendar/?search_period=custom&start_date=2015-01-01&end_date=2017-12-31&output_format=compact' % (coursecode))
        url = br.open('https://www.kth.se/social/course/%s/other_subgroups/' % (coursecode))

        courselink = "/social/course/"
        courselink = courselink + coursecode
        courselink1 = courselink + "/other_subgroups/"
        courselink2 = courselink + "/subgroup/"

        beautyurl = BeautifulSoup(url)
        links1 = beautyurl.find_all('a', href=lambda value: value and value.startswith(courselink1))
        links2 = beautyurl.find_all('a', href=lambda value: value and value.startswith(courselink2))




        url = br.open('https://www.kth.se/social/course/%s/other_subgroups/' % (coursecode))

        beautyurl = BeautifulSoup(url)
        links3 = beautyurl.find_all('a', href=lambda value: value and value.startswith(courselink1))
        links4 = beautyurl.find_all('a', href=lambda value: value and value.startswith(courselink2))

        linksvar = links1 + links2 + links3 + links4

        for idx, item in enumerate(linksvar):
            #print "outer"
            yeartext = "-" + str(year) + "-"
            if yeartext in item['href']:
                fullcourselink = "https://www.kth.se"
                fullcourselink = fullcourselink + item['href']
                # print idx
                print fullcourselink
                url = br.open(fullcourselink)

                schedulexml = BeautifulSoup(url)
                schedulexml = schedulexml.find('a', text="Schema")

                schedulelink = "https://www.kth.se"
                schedulelink = schedulelink + schedulexml['href']

                url = br.open(schedulelink)

                slotsxml = BeautifulSoup(url)
                slotsxml1 = slotsxml.find_all('a', href=lambda value: value and value.startswith(courselink1))
                slotsxml2 = slotsxml.find_all('a', href=lambda value: value and value.startswith(courselink2))
                slotsxml = slotsxml1 + slotsxml2
                # print xml

                for idx, item in enumerate(slotsxml):
                    #print "inner"
                    # print idx
                    #print item['href']
                    if "event" in item['href']:
                        # linklist.append(item['href'])
                        linkvar = item['href']
                        testlink = "https://www.kth.se"
                        testlink = testlink + linkvar
                        print coursecode, "FETCHING SLOT", testlink
                        url = br.open(testlink)

                        # xml = BeautifulSoup(src)
                        xml = BeautifulSoup(url)
                        # testlist = xml.find_all('a', { "class" : "fancybox" })

                        startdate = xml.find('span', itemprop=lambda value: value and value.startswith("startDate"))
                        startdate = startdate.text
                        # print startdate
                        enddate = xml.find('span', itemprop=lambda value: value and value.startswith("endDate"))
                        enddate = enddate.text
                        # print enddate

                        datevar = startdate[:10]
                        # print datevar

                        yearvar = int(startdate[:4])

                        yearvar = courseyear_from_classdate(coursecode, yearvar, datevar)
                        # print yearvar
                        codevar = testlink[33:39]
                        # print codevar
                        starttimevar = startdate[11:13]
                        # print starttimevar
                        endtimevar = enddate[11:13]
                        # print endtimevar

                        #templist = db.session.query(Courses).all()
                        # for item in templist:
                        #    print item.year

                        roomobj = None

                        courseobj = create_or_fetch_courseobj(codevar, year)
                        # term = what_term_is_this(datevar)
                        # db.session.commit()
                        # print courseobj.code
                        # print "hej"

                        dateobj = create_or_fetch_dateobj(datetime.datetime.strptime(datevar, "%Y-%m-%d"))
                        create_course_date_connection(courseobj, dateobj)

                        classobj = create_or_fetch_classobj(starttimevar, endtimevar, courseobj, dateobj)

                        locations = xml.find_all('a', href=lambda value: value and value.startswith("https://www.kth.se/places/room"))

                        for location in locations:
                            # print "location"

                            locationname = location.text
                            locationlink = location['href']
                            # print location.text, "FETCHING ROOM", location['href']
                            # print location
                            # print codevar
                            # print yearvar

                            roomobj = create_or_fetch_roomobj(locationname, locationlink)
                            create_room_date_connection(roomobj, dateobj)

                            # kolla vidare classobject - det ballar ur

                            # print "xxx"
                            # print classobj.starttime
                            create_room_class_connection(roomobj, classobj)





    return "DONE"


# Adding slots from Social for all courses
@app.route('/xslotsfromapiandsocial')
def xslotsfromsocial():
    # print "YO"
    linklist = []

    br = open_password_protected_site("https://login.kth.se/login/")

    # testcourse = ["AI2808"]

    templist = allcourses()
    # templist = templist[:50]
    for idx, item in enumerate(templist):
        # for idx, item in enumerate(testcourse):
        coursecode = item.code
        # coursecode = "AI2808"
        # Fetching slots from schedule API

        tempdict = {}

        # tempdict = fetchinglistofslotspercourse(coursecode, "2015-01-01", "2018-06-30")
        # parselistofslotspercourse(tempdict)

        try:
            url = br.open('https://www.kth.se/social/course/%s/subgroup/' % (coursecode))

            courselink = "/social/course/"
            courselink = courselink + coursecode
            courselink = courselink + "/subgroup/"

        except Exception, e:
            varcode = "no subgroup on social"
            print varcode
            print coursecode

            try:
                url = br.open('https://www.kth.se/social/course/%s/other_subgroups/' % (coursecode))

                courselink = "/social/course/"
                courselink = courselink + coursecode
                courselink = courselink + "/other_subgroups/"

            except Exception, e:
                varcode = "no other subgroups on social"
                print varcode
                print coursecode
                # session.rollback()
                # raise
                continue


        url = br.open('https://www.kth.se/social/course/%s/calendar/?search_period=custom&start_date=2015-01-01&end_date=2017-12-31&output_format=compact' % (coursecode))

        courselink = "/social/course/"
        courselink = courselink + coursecode
        courselink1 = courselink + "/other_subgroups/"
        courselink2 = courselink + "/subgroup/"

        xml = BeautifulSoup(url)
        xml1 = xml.find_all('a', href=lambda value: value and value.startswith(courselink1))
        xml2 = xml.find_all('a', href=lambda value: value and value.startswith(courselink2))
        xml = xml1 + xml2

        for idx, item in enumerate(xml):
            print "outer"
            # print idx
            try:
                fullcourselink = "https://www.kth.se"
                fullcourselink = fullcourselink + item['href']
                # print idx
                print fullcourselink
                url = br.open(fullcourselink)

                xml = BeautifulSoup(url)
                xml = xml.find('a', text="Schema")

                schedulelink = "https://www.kth.se"
                schedulelink = schedulelink + xml['href']

                url = br.open(schedulelink)

                xml = BeautifulSoup(url)
                xml1 = xml.find_all('a', href=lambda value: value and value.startswith(courselink1))
                xml2 = xml.find_all('a', href=lambda value: value and value.startswith(courselink2))
                xml = xml1 + xml2
                # print xml
                for idx, item in enumerate(xml):
                    # print "inner"
                    # print idx
                    # print item['href']
                    if "event" in item['href']:
                        # linklist.append(item['href'])
                        linkvar = item['href']
                        print "FETCHING SLOT"
                        print coursecode
                        testlink = "https://www.kth.se"
                        testlink = testlink + linkvar
                        print testlink
                        url = br.open(testlink)

                        # xml = BeautifulSoup(src)
                        xml = BeautifulSoup(url)
                        # testlist = xml.find_all('a', { "class" : "fancybox" })

                        startdate = xml.find('span', itemprop=lambda value: value and value.startswith("startDate"))
                        startdate = startdate.text
                        # print startdate
                        enddate = xml.find('span', itemprop=lambda value: value and value.startswith("endDate"))
                        enddate = enddate.text
                        # print enddate

                        datevar = startdate[:10]
                        # print datevar

                        yearvar = pass_courseyear_from_classdate(datevar)
                        # print yearvar
                        codevar = testlink[33:39]
                        # print codevar
                        starttimevar = startdate[11:13]
                        # print starttimevar
                        endtimevar = enddate[11:13]
                        # print endtimevar

                        #templist = db.session.query(Courses).all()
                        # for item in templist:
                        #    print item.year

                        roomobj = None

                        courseobj = create_or_fetch_courseobj(codevar, yearvar)
                        # term = what_term_is_this(datevar)
                        # db.session.commit()
                        # print courseobj.code
                        # print "hej"

                        dateobj = create_or_fetch_dateobj(datevar)
                        create_course_date_connection(courseobj, dateobj)

                        locations = xml.find_all('a', href=lambda value: value and value.startswith("https://www.kth.se/places/room"))

                        for location in locations:
                            # print "location"
                            try:
                                # print location
                                location = location.text
                                print "FETCHING ROOM"
                                # print location
                                # print codevar
                                # print yearvar

                                roomobj = create_or_fetch_roomobj(location)
                                create_room_date_connection(roomobj, dateobj)

                                # kolla vidare classobject - det ballar ur
                                classobj = create_or_fetch_classobj(starttimevar, endtimevar, courseobj, dateobj)
                                # print "xxx"
                                # print classobj.starttime
                                create_room_class_connection(roomobj, classobj)

                            except Exception, e:
                                varcode = "NO ROOM"
                                print varcode
                                classobj = create_or_fetch_classobj(starttimevar, endtimevar, courseobj, dateobj)
                                # print "yyy"
                                # print classobj.starttime
                                # create_room_class_connection(roomobj, classobj)
                                continue
            except Exception, e:
                varcode = "No schedule"
                print varcode
                print coursecode
                # session.rollback()
                # raise
                continue



    return "DONE"






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
