from app import app, db
import requests
from functions import createtables, courseinfoperyearandterm, staffperdepartment, teachersfromdepartment, create_or_fetch_teacherobj
from functions import create_or_fetch_courseobj, coursesfromdepartment2, addcoursestotables_first
from functions import coursesfromdepartment3, jsonifycoursesfromdepartment, fetchinglistofcodesfordepartmentcourses




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
        tempdict = staffperdepartment(item)
        templist.append(tempdict)

    # ADD_ALL_TEACHERS_IN_LIST_TO_DB
    teachersfromdepartment(templist)


    # ADD_ALL_COURSES_TO_DB
    tempdict = {}
    templist = []


    # tempdict20151 = courseinfoperyearandterm(2015, 1)
    # tempdict20152 = courseinfoperyearandterm(2015, 2)
    # tempdict20161 = courseinfoperyearandterm(2016, 1)
    tempdict20162 = courseinfoperyearandterm(2016, 2)
    tempdict20171 = courseinfoperyearandterm(2017, 1)




    # addcoursestotables_first(tempdict20151)
    # addcoursestotables_first(tempdict20152)
    # addcoursestotables_first(tempdict20161)
    addcoursestotables_first(tempdict20162)
    addcoursestotables_first(tempdict20171)


    # ADD_ALL_COURSES_TO_DB
    for item in departments:
        tempdict = fetchinglistofcodesfordepartmentcourses(item)
        templist.append(jsonifycoursesfromdepartment(tempdict))
    coursesfromdepartment3(templist)


    return "restartall"




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
