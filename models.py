import datetime
from app import db
from sqlalchemy import UniqueConstraint



teachers_classes = db.Table('teachers_classes',
                            db.Column('teachers_id', db.Integer, db.ForeignKey('teachers.id')),
                            db.Column('classes_id', db.Integer, db.ForeignKey('classes.id')),
                            UniqueConstraint('teachers_id', 'classes_id')
                            )

rooms_classes = db.Table('rooms_classes',
                         db.Column('rooms_id', db.Integer, db.ForeignKey('rooms.id')),
                         db.Column('classes_id', db.Integer, db.ForeignKey('classes.id')),
                         UniqueConstraint('rooms_id', 'classes_id')
                         )

dates_courses = db.Table('dates_courses',
                         db.Column('dates_id', db.Integer, db.ForeignKey('dates.id')),
                         db.Column('courses_id', db.Integer, db.ForeignKey('courses.id'))
                         )

dates_rooms = db.Table('dates_rooms',
                       db.Column('dates_id', db.Integer, db.ForeignKey('dates.id')),
                       db.Column('rooms_id', db.Integer, db.ForeignKey('rooms.id'))
                       )


dates_teachers = db.Table('dates_teachers',
                          db.Column('dates_id', db.Integer, db.ForeignKey('dates.id')),
                          db.Column('teachers_id', db.Integer, db.ForeignKey('teachers.id'))
                          )


subjects_classes = db.Table('subjects_classes',
                            db.Column('subjects_id', db.Integer, db.ForeignKey('subjects.id')),
                            db.Column('classes_id', db.Integer, db.ForeignKey('classes.id'))
                            )


# One-to-many. Parent to Rooms
class Roomtypes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    roomtype = db.Column(db.String(30), unique=True)
    cost = db.Column(db.Integer)
    rooms = db.relationship('Rooms', backref='roomtypes', lazy='dynamic')


# One-to-many. Child to Roomtypes
class Rooms(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    seats = db.Column(db.Integer)
    roomtypes_id = db.Column(db.Integer, db.ForeignKey('roomtypes.id'))
    classes = db.relationship('Classes', secondary=rooms_classes, backref=db.backref('rooms', lazy='dynamic'))
    notourclasses = db.relationship('Notourclasses', backref='rooms', lazy='dynamic')


class Subjects(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    classes = db.relationship('Classes', secondary=subjects_classes, backref=db.backref('subjects', lazy='dynamic'))


class Dates(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, unique=True)
    courses = db.relationship('Courses', secondary=dates_courses, backref=db.backref('dates', lazy='dynamic'))
    rooms = db.relationship('Rooms', secondary=dates_rooms, backref=db.backref('dates', lazy='dynamic'))
    teachers = db.relationship('Teachers', secondary=dates_teachers, backref=db.backref('dates', lazy='dynamic'))
    classes = db.relationship('Classes', backref='dates', lazy='dynamic')


class Teachers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(30))
    akafirstname = db.Column(db.String(100))
    akalastname = db.Column(db.String(30))
    email = db.Column(db.String(50), unique=True)
    initials = db.Column(db.String(3), unique=True)
    password = db.Column(db.String(30))
    kthid = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(50), unique=True)
    department = db.Column(db.String(100))
    examiner = db.relationship('Courses', backref='examiner', lazy='dynamic', foreign_keys='[Courses.examiner_id]')
    responsible = db.relationship('Courses', backref='responsible', lazy='dynamic', foreign_keys='[Courses.responsible_id]')
    assistantone = db.relationship('Courses', backref='assistantone', lazy='dynamic', foreign_keys='[Courses.assistantone_id]')
    assistanttwo = db.relationship('Courses', backref='assistanttwo', lazy='dynamic', foreign_keys='[Courses.assistanttwo_id]')
    classes = db.relationship('Classes', secondary=teachers_classes, backref=db.backref('teachers', lazy='dynamic'))


class Courses(db.Model):
    __table_args__ = (db.UniqueConstraint('code', 'year'),
                      )
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    code = db.Column(db.String(30))
    schedule_exists = db.Column(db.Boolean, default=False)
    year = db.Column(db.Integer)
    term = db.Column(db.Integer)
    period = db.Column(db.Integer)
    roundid = db.Column(db.Integer)
    studentsexpected = db.Column(db.Integer)
    studentsregistred = db.Column(db.Integer)
    startweek = db.Column(db.String(30))
    endweek = db.Column(db.String(30))
    classes = db.relationship('Classes', cascade='all, delete, delete-orphan', backref='courses', lazy='dynamic')
    examiner_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    responsible_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    assistantone_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    assistanttwo_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    # UniqueConstraint('code', 'year')


class Classtypes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    classtype = db.Column(db.String(30), unique=True)
    classes = db.relationship('Classes', backref='classtypes', lazy='dynamic')


class Classes(db.Model):
    __table_args__ = (db.UniqueConstraint('starttime', 'endtime', 'courses_id', 'dates_id'),
                      )
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(100))
    contentapi = db.Column(db.String(100))
    info = db.Column(db.String(500))
    starttime = db.Column(db.Integer, nullable=False)
    endtime = db.Column(db.Integer, nullable=False)
    courses_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    dates_id = db.Column(db.Integer, db.ForeignKey('dates.id'), nullable=False)
    classtypes_id = db.Column(db.Integer, db.ForeignKey('classtypes.id'))
    # __table_args__ = (db.UniqueConstraint('starttime', 'endtime', 'courses_id', 'dates_id),)
    # UniqueConstraint('starttime', 'endtime', 'courses_id', 'dates_id')



class Notourclasses(db.Model):
    __table_args__ = (db.UniqueConstraint('startdate', 'enddate', 'endtime', 'starttime', 'lastchangeddate', 'lastchangedtime', 'status', 'room_id'),
                      )
    id = db.Column(db.Integer, primary_key=True)
    startdate = db.Column(db.DateTime, nullable=False)
    enddate = db.Column(db.DateTime, nullable=False)
    starttime = db.Column(db.String(3), nullable=False)
    endtime = db.Column(db.String(3), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'))
    status = db.Column(db.String(100), nullable=False)
    lastchangeddate = db.Column(db.DateTime, nullable=False)
    lastchangedtime = db.Column(db.String(3), nullable=False)
    # __table_args__ = (db.UniqueConstraint('starttime', 'endtime', 'courses_id', 'dates_id),)
    # UniqueConstraint('starttime', 'endtime', 'courses_id', 'dates_id')


class RegistrationForm(Form):
    initials = TextField('Initials', [validators.Length(min=2, max=20)])
    firstname = TextField('First name', [validators.Length(min=2, max=20)])
    lastname = TextField('Last name', [validators.Length(min=2, max=30)])
    email = TextField('Email Address', [validators.Length(min=7, max=50)])
    password = PasswordField('New Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    # accept_tos = BooleanField('I accept the Terms of Service and Privacy Notice (updated Jan 22, 2015)', [validators.Required()])

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    pets = db.relationship('Pet', backref='owner', lazy='dynamic')

class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    owner_id = db.Column(db.Integer, db.ForeignKey('person.id'))
