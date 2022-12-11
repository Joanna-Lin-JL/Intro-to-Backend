
from db import db
from db import Course
from db import Assignment
from db import User
from flask import Flask
from flask import request
import json
import os

app = Flask(__name__)
db_filename = "cms.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()


def success_response(data, code=200):
    """ 
    Generalize the success response formats
    """
    return json.dumps(data), code


def failure_response(message, code=404):
    """
    Generalize the failure response formats
    """
    return json.dumps({"error": message}), code


def get_course_helper(course_id):
    """
    Helper function to get a course by id
    """
    return Course.query.filter_by(id=course_id).first()


@app.route("/")
def greeting(): 
    """
    Endpoint for greeting user by reading from .env file
    """
    return os.environ["NETID"] + " was here!"

@ app.route("/api/courses/")
def get_courses():
    """
    Endpoint to get all courses
    """
    courses = []
    for c in Course.query.all():
        courses.append(c.serialize())
    return success_response({"courses": courses})


@ app.route("/api/courses/", methods=["POST"])
def create_course():
    """
    Endpoint to create a course
    """
    body = json.loads(request.data)
    code = body.get('code')
    if code is None:
        return failure_response("code not inputted", 400)
    name = body.get('name')
    if name is None:
        return failure_response("name not inputted", 400)
    new_course = Course(
        code=code,
        name=name,
        assignments=[],
        instructors=[],
        students=[]
    )
    db.session.add(new_course)
    db.session.commit()
    return success_response(new_course.serialize(), 201)


@ app.route("/api/courses/<int:course_id>/")
def get_course(course_id):
    """
    Endpoint to get a specific course by course id
    """
    course = get_course_helper(course_id)
    if course is None:
        return failure_response("Course not found!")
    return success_response(course.serialize())


@ app.route("/api/courses/<int:course_id>/", methods=['DELETE'])
def delete_course(course_id):
    """
    Endpoint to delete a course by its id
    """
    course = get_course_helper(course_id)
    if course is None:
        return failure_response("Course not found!")
    db.session.delete(course)
    db.session.commit()
    return success_response(course.serialize())


@ app.route("/api/users/", methods=['POST'])
def create_user():
    """
    Endpoint to create an user
    """
    body = json.loads(request.data)
    name = body.get('name')
    if name is None:
        return failure_response("name not inputted", 400)
    netid = body.get('netid')
    if netid is None:
        return failure_response("netid not inputted", 400)
    new_user = User(
        name=name,
        netid=netid,
        instruct_courses=[],
        student_courses=[]
    )
    db.session.add(new_user)
    db.session.commit()
    return success_response(new_user.serialize(), 201)


@ app.route("/api/users/<int:user_id>/")
def get_user(user_id):
    """
    Endpoint to get a user by id
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found!")
    return success_response(user.serialize())


@ app.route("/api/courses/<int:course_id>/add/", methods=['POST'])
def add_user_to_course(course_id):
    """
    Endpoint to add a user to a course
    """
    course = get_course_helper(course_id)
    if course is None:
        return failure_response("Course not found!")

    body = json.loads(request.data)
    user_id = body.get('user_id')
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found!")

    type = body.get('type')
    if type == "student":
        course.students.append(user)
    elif type == "instructor":
        course.instructors.append(user)
    else:
        return failure_response("Type not correct!", 400)
    db.session.commit()
    return success_response(course.serialize(), 200)


@ app.route("/api/courses/<int:course_id>/assignment/", methods=['POST'])
def create_assignment(course_id):
    """
    Endpoint to create an assignment for a course
    """
    course = get_course_helper(course_id)
    if course is None:
        return failure_response("Course not found!")

    body = json.loads(request.data)

    title = body.get('title')
    if title is None:
        return failure_response("Title not inputted", 400)

    due_date = body.get('due_date')
    if due_date is None:
        return failure_response("Due Date not inputted", 400)

    new_assignment = Assignment(
        title=title,
        due_date=due_date,
        course=course_id
    )

    db.session.add(new_assignment)
    db.session.commit()
    return success_response(new_assignment.serialize(), 201)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
