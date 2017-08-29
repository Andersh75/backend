from app import app, db
import requests
from functions_collect_teachers import staffperdepartment, teachersfromdepartment
from functions_collect_courses import coursesfromdepartment3, jsonifycoursesfromdepartment, fetchinglistofcodesfordepartmentcourses, coursesfromdepartment2, addcoursestotables_first, coursecodeandroundidperyearandterm
from functions import open_password_protected_site, createtables, allcourses, create_or_fetch_roomobj_without_link, create_or_fetch_notourclassobj, create_coursefacts_course_connection, create_course_date_connection, create_room_class_connection, create_room_date_connection, create_or_fetch_hourobj, create_or_fetch_classobj, create_or_fetch_courseobj, create_or_fetch_coursefactsobj, create_or_fetch_dateobj, create_or_fetch_roomobj, create_or_fetch_teacherobj, fetch_courseobj
from functions_collect_slots import courseyear_from_classdate, fetchinglistofslotspercourse, parselistofslotspercourse
from app import db
import urllib
import urllib2
from urllib2 import urlopen
from bs4 import BeautifulSoup
import re
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
    # departments = ["AID"]
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
    # tempdict20151 = coursecodeandroundidperyearandterm(2015, 1)
    # tempdict20152 = coursecodeandroundidperyearandterm(2015, 2)
    # tempdict20161 = coursecodeandroundidperyearandterm(2016, 1)
    # tempdict20162 = coursecodeandroundidperyearandterm(2016, 2)
    tempdict20171 = coursecodeandroundidperyearandterm(2017, 1)
    tempdict20172 = coursecodeandroundidperyearandterm(2017, 2)


    # ROUND ID IS LIKE PART ONE OR TWO OF TERM
    # COLLECT STARTWEEK, ENDWEEK, PERIODS AND COURSE RESPONSIBLE
    # ADD COURSE TO DB - NO INFO ON EXAMINER YET
    # addcoursestotables_first(tempdict20151)
    # addcoursestotables_first(tempdict20152)
    # addcoursestotables_first(tempdict20161)
    # addcoursestotables_first(tempdict20162)
    addcoursestotables_first(tempdict20171)
    addcoursestotables_first(tempdict20172)

    # print "XXXXXX"

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

    # templist = []

    # templist.append(fetch_courseobj('AI2808', 2017))

    templist = allcourses()
    # templist = testcourse
    for idx, item in enumerate(templist):
        # for idx, item in enumerate(testcourse):
        coursecode = item.code
        year = item.year
        # Fetching slots from schedule API
        print coursecode

        startdate = item.startdate

        print "startdate: ",startdate.strftime("%Y-%m-%d")

        enddate = startdate + timedelta(days=365)

        print "enddate: ",enddate.strftime("%Y-%m-%d")

        tempdict = {}
        tempdict = fetchinglistofslotspercourse(coursecode, startdate.strftime("%Y-%m-%d"), enddate.strftime("%Y-%m-%d"))

        try:
            parselistofslotspercourse(tempdict)
        except Exception, e:
            varcode = "CORRUPT"
            print coursecode

    return "DONE"



@app.route('/bookedfromapiold')
def bookedfromapiold():
    '''
    db.drop_all()
    db.session.commit()

    createtables()
    '''

    tempdict = {}
    templist = []

    j = urllib2.urlopen('http://www.kth.se/api/timetable/v1/reservations/search?start=2017-08-31T10:00:00&end=2017-11-01T10:00:00')

    j_obj = json.load(j)


    for item in j_obj:
        try:
            print item['id']
        except Exception, e:
            varcode = "NO ID"
            print varcode


        try:
            print item['start']
            starthour = int(item['start'][11:13])
        except Exception, e:
            varcode = "NO START"
            print varcode


        try:
            print item['end']
            endhour = int(item['end'][11:13])
        except Exception, e:
            varcode = "NO END"
            print varcode


        duration = endhour - starthour

        print "DURATION", duration

        hours = []

        # hours.append(starthour)

        i = 0

        while i < duration:
            hours.append(starthour + i)
            i = i + 1

        print "HOURS: ", hours



        try:
            print item['lastchanged']
        except Exception, e:
            varcode = "NO LASTCHANGED"
            print varcode

        try:
            print item['lastrevised']
        except Exception, e:
            varcode = "NO LASTREVISITED"
            print varcode


        try:
            for location in item['locations']:
                print location['name']
        except Exception, e:
            varcode = "NO LOCATIONS"
            print varcode



        try:
            print item['status']
        except Exception, e:
            varcode = "NO STATUS"
            print varcode


        bookedroomobj = None

        if item['id']:
            #print int(starttimevar)
            #print endtimevar
            #print courseobj.id
            #print dateobj.id
            bookedroomssubq = db.session.query(Bookedrooms).filter(Bookedrooms.id == item['id'])
            alreadybookedroom = db.session.query(bookedroomssubq.exists()).scalar()

            #test = db.session.query(Classes).join(Classes.courses).join(Classes.rooms).join(Classes.dates).filter(and_(Courses.id == 70, Dates.id == 306, Classes.starttime == 8, Classes.endtime == 10)).first()
            # print test

            if alreadybookedroom:
                print "BOOKEDROOMSOBJECT FETCHED"
                bookedroomobj = bookedroomssubq.first()
            else:
                print "NO PREVIOUS BOOKEDROOMSOBJECT"

                try:
                    tempdict = {}
                    tempdict['number'] = item['id']
                    tempdict['name'] = item['locations'][0]['name']
                    tempdict['start'] = item['start']
                    tempdict['end'] = item['end']
                    tempdict['lastchanged'] = item['lastchanged']
                    tempdict['lastrevised'] = item['lastrevised']
                    tempdict['status'] = item['status']

                    record = Bookedrooms(**tempdict)
                    bookedroomobj = record
                    db.session.add(record)
                    db.session.commit()
                    print "CREATED BOOKEDROOMSOBJECT"

                except Exception, e:
                    varcode = "SOMETHING WENT WRONG"
                    print varcode

            for hour in hours:
                hourobj = create_or_fetch_hourobj(hour)

                if (item['status'] == "Cancelled"):
                    print "CANCELLED"
                    remove_bookedroom_hour_connection(bookedroomobj, hourobj)
                # else:
                    # create_bookedroom_hour_connection(bookedroomobj, hourobj)




        else:
            print "NO ID"




    return "DONE"


@app.route('/bookedfromapi')
def bookedfromapi():
    '''
    db.drop_all()
    db.session.commit()

    createtables()
    '''

    tempdict = {}
    templist = []

    j = urllib2.urlopen('http://www.kth.se/api/timetable/v1/reservations/search?start=2017-08-28T10:00:00&end=2017-10-28T12:00:00')

    j_obj = json.load(j)


    for item in j_obj:
        '''
        try:
            print item['id']
        except Exception, e:
            varcode = "NO ID"
            print varcode
        '''


        try:
            starthour = int(item['start'][11:13])
            startdate = item['start'][:10]
            #print "starthour: ", starthour
            #print "startdate: ", startdate
        except Exception, e:
            varcode = "NO START"
            print varcode


        try:
            endhour = int(item['end'][11:13])
            enddate = item['end'][:10]
            #print "endhour: ", endhour
            #print "enddate: ", enddate
        except Exception, e:
            varcode = "NO END"
            print varcode


        duration = endhour - starthour

        #print "DURATION", duration

        hours = []

        # hours.append(starthour)

        i = 0

        while i < duration:
            hours.append(starthour + i)
            i = i + 1

        #print "HOURS: ", hours


        '''
        try:
            print item['lastchanged']
        except Exception, e:
            varcode = "NO LASTCHANGED"
            print varcode

        try:
            print item['lastrevised']
        except Exception, e:
            varcode = "NO LASTREVISITED"
            print varcode
        '''


        try:
            print item['status']
            status = item['status']
        except Exception, e:
            varcode = "NO STATUS"
            print varcode


        #try:
        for location in item['locations']:
            #print location['name']
            roomvar = location['name']
            dateobj = create_or_fetch_dateobj(datetime.datetime.strptime(startdate, "%Y-%m-%d"))

            roomobj = create_or_fetch_roomobj_without_link(roomvar)
            #print roomobj.name

            for hour in hours:
                hourobj = create_or_fetch_hourobj(hour)
                #print "BEFORE"
                #print roomobj.name
                #print roomobj.id
                # print dateobj.id
                notourclassobj = create_or_fetch_notourclassobj(dateobj, hourobj, roomobj)
                #print "CREATED: ", notourclassobj.id
                if (status == "Cancelled"):
                    print "DELETED: ", notourclassobj.id
                    db.session.delete(notourclassobj)
                    db.session.commit()


        #except Exception, e:
            #varcode = "NO LOCATIONS"
            #print varcode



        '''


        try:
            for staff in item['staffs']:
                print staff['kthId']
        except Exception, e:
            varcode = "NO STAFFS"
            print varcode


        try:
            print item['department']['code']
        except Exception, e:
            varcode = "NO DEPARTMENT"
            print varcode


        try:
            for program in item['programmes']:
                print program['code']
        except Exception, e:
            varcode = "NO PROGRAMMES"
            print varcode


        try:
            for course in item['courses']:
                print course['id']
        except Exception, e:
            varcode = "NO COURSES"
            print varcode
        # print item['offerings']

        try:
            print item['description']
        except Exception, e:
            varcode = "NO DESCRIPTION"
            print varcode

        try:
            print item['department']['name']
        except Exception, e:
            varcode = "NO DEPARTMENT"
            print varcode


        try:
            print item['typedesc']
        except Exception, e:
            varcode = "NO TYPEDESC"
            print varcode


        try:
            print item['typename']
        except Exception, e:
            varcode = "NO TYPENAME"
            print varcode
        '''


    return "DONE"



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


# Link programs to courses
@app.route('/trying')
def trying():


    templist = allcourses()

    for item in templist:

        req = urllib2.urlopen('https://www.kth.se/student/kurser/kurs/%s?startterm=%s%s' % (item.code, item.year, item.term))

        xml = BeautifulSoup(req)

        xml = xml.find_all("div", id=lambda value: value and value.startswith(str(item.year)))


        tgroup = ""
        tprogram = ""

        for courseround in xml:

            group = courseround.find(text=re.compile('grupp'))

            if group:
                targetgroup = group.parent.findNext('p')

                if targetgroup:

                    tgroup = tgroup + targetgroup.contents[0] + ";"



            program = courseround.find(text=re.compile('Del av program'))



            if program:

                partofprogram = program.parent.findNext('ul')

                if partofprogram:

                    partofprogram = partofprogram.findAll('a')

                    mystring = ""

                    for linkitem in partofprogram:

                        freetochoosevar = False
                        recommendedvar = False
                        mandatoryvar = False
                        uppdragvar = False
                        openvar = False
                        yearvar = 0
                        namevar = "None"

                        mystring = mystring + linkitem.contents[0] + ";"

                        if "andidatprogram" in linkitem.contents[0]:
                            if "och finans" in linkitem.contents[0]:
                                namevar = "TFOFK"
                            if "utveckling" in linkitem.contents[0]:
                                namevar = "TFAFK"
                        if "asterprogram" in linkitem.contents[0]:
                            if "byggande" in linkitem.contents[0]:
                                namevar = "TFOBM"
                            else:
                                namevar = "Other"

                        if "ivilingenj" in linkitem.contents[0]:
                            namevar = "CSAMH"
                        if "1" in linkitem.contents[0]:
                            yearvar = 1
                        if "2" in linkitem.contents[0]:
                            yearvar = 2
                        if "3" in linkitem.contents[0]:
                            yearvar = 3

                        if "valfri" in linkitem.contents[0]:
                            freetochoosevar = True
                        if "ekommender" in linkitem.contents[0]:
                            recommendedvar = True
                        if "bligatorisk" in linkitem.contents[0]:
                            mandatoryvar = True

                        # if "ppdragsutb" in linkitem.contents[0]:
                        #    uppdragvar = True
                        # if "ppdragsutb" in tgroup:
                        #    uppdragvar = True
                        # if "alla program" in tgroup:
                        #    openvar = True

                        coursefactsobj = create_or_fetch_coursefactsobj(namevar, freetochoosevar, mandatoryvar, recommendedvar, yearvar, uppdragvar, openvar)

                        create_coursefacts_course_connection(coursefactsobj, item)

                    tprogram = tprogram + mystring


        item.targetgroup = tgroup

        item.partofprogram = tprogram

        db.session.commit()










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
