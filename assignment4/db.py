from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

association_table_instructor = db.Table("association_instructor", db.Model.metadata,
                                        db.Column("course_id", db.Integer,
                                                  db.ForeignKey("course.id")),
                                        db.Column("user_id", db.Integer, db.ForeignKey("user.id")))

association_table_student = db.Table("association_student", db.Model.metadata,
                                     db.Column("course_id", db.Integer,
                                               db.ForeignKey("course.id")),
                                     db.Column("user_id", db.Integer, db.ForeignKey("user.id")))


class Course(db.Model):
    __tablename__ = "course"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    assignments = db.relationship("Assignment", cascade="delete")

    instructors = db.relationship(
        "User", secondary=association_table_instructor, back_populates="instruct_courses")
    students = db.relationship(
        "User", secondary=association_table_student, back_populates="student_courses")

    def serialize(self):
        """
        Serializes information from Course table
        """
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "assignments": [a.serialize_short() for a in self.assignments],
            "instructors": [i.serialize_short() for i in self.instructors],
            "students": [s.serialize_short() for s in self.students]
        }

    def serialize_short(self):
        """
        Serializes information from Course table without assignments, instructors, and students
        """
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name
        }


class Assignment(db.Model):
    __tablename__ = "assignment"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    due_date = db.Column(db.BigInteger, nullable=False)
    course = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)

    def serialize(self):
        """
        Serializes information from the Assignment table
        """
        return {
            "id": self.id,
            "title": self.title,
            "due_date": self.due_date,
            "course": Course.query.filter_by(id=self.course).first().serialize_short()
        }

    def serialize_short(self):
        """
        Serializes information from the Assignment table without courses
        """
        return {
            "id": self.id,
            "title": self.title,
            "due_date": self.due_date
        }


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    netid = db.Column(db.String, nullable=False)
    instruct_courses = db.relationship(
        "Course", secondary=association_table_instructor, back_populates='instructors')
    student_courses = db.relationship(
        "Course", secondary=association_table_student, back_populates='students')

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "netid": self.netid,
            "courses": ([c.serialize_short() for c in self.instruct_courses] + [b.serialize_short() for b in self.student_courses])
        }

    def serialize_short(self):
        return {
            "id": self.id,
            "name": self.name,
            "netid": self.netid
        }
