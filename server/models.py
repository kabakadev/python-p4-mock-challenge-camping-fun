from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


class Activity(db.Model, SerializerMixin):
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    difficulty = db.Column(db.Integer)

    signups = db.relationship('Signup', back_populates='activity', cascade="all, delete-orphan")

    serialize_rules = ('-signups.activity',)

    def __repr__(self):
        return f'<Activity {self.id}: {self.name}>'


class Camper(db.Model, SerializerMixin):
    __tablename__ = 'campers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer)

    signups = db.relationship('Signup', back_populates='camper', cascade='all, delete-orphan')

    def to_dict(self,include_signups=False):
        camper_dict = {
            "id":self.id,
            "name":self.name,
            "age":self.age,
        }
        if include_signups:
            camper_dict["signups"] = [
                signup.to_dict() for signup in self.signups
            ]
        return camper_dict
    # serialize_only = ('id','name','age')
    serialize_rules = ('-signups.camper',)


    @validates('name')
    def validate_name(self, key, name):
        if not name or not name.strip():
            raise ValueError("Camper name must not be empty")
        return name

    @validates('age')
    def validate_age(self, key, age):
        if not (8 <= age <= 18):
            raise ValueError("Camper age must be between 8 and 18")
        return age

    def __repr__(self):
        return f'<Camper {self.id}: {self.name}>'


class Signup(db.Model, SerializerMixin):
    __tablename__ = 'signups'

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer)

    camper_id = db.Column(db.Integer, db.ForeignKey('campers.id'), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), nullable=False)

    activity = db.relationship('Activity', back_populates='signups')
    camper = db.relationship('Camper', back_populates='signups')

    serialize_rules = ('-activity.signups', '-camper.signups')

    @validates('time')
    def validate_time(self, key, time):
        if not (0 <= time <= 23):
            raise ValueError("Time must be between 0 and 23")
        return time

    def __repr__(self):
        return f'<Signup {self.id}>'
