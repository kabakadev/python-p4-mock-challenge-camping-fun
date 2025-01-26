#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''

@app.route('/campers', methods=['GET','POST'])
def campers():
    if request.method == 'GET':
        campers=Camper.query.all()
        return make_response([camper.to_dict() for camper in campers]),200
    elif request.method == 'POST':
        data = request.get_json()
        try:
            camper = Camper(name=data['name'],age=data['age'])
            db.session.add(camper)
            db.session.commit()
            return make_response(camper.to_dict()),201
        except Exception as e:
            return make_response({"errors":["validation errors"]}),400

@app.route('/campers/<int:id>', methods=['GET','PATCH'])
def camper_detail(id):
    camper = Camper.query.get(id)
    if not camper:
        return make_response({"error":"Camper not found"}),404
    if request.method == 'GET':
        return make_response(camper.to_dict(include_signups=True)),200
    elif request.method == 'PATCH':
        data = request.get_json()
        try:
            if 'name' in data:
                camper.name = data['name']
            if 'age' in data:
                camper.age = data['age']
            db.session.commit()
            return make_response(camper.to_dict()),202
        except Exception as e:
            return make_response({"errors":["validation errors"]}),400
@app.route('/activities', methods=['GET'])
def activities():
    activities = Activity.query.all()
    return make_response([activity.to_dict() for activity in activities]),200

@app.route('/activities/<int:id>', methods=['DELETE'])
def delete_activity(id):
    activity = Activity.query.get(id)
    if not activity:
        return make_response({"error":"Activity not found"}),404
    try:
        db.session.delete(activity)
        db.session.commit()
        return '',204
    except Exception as e:
        return make_response({"error":str(e)}),500
    
@app.route('/signups', methods=['POST'])
def signups():
    data = request.get_json()
    try:
        signup = Signup(
            camper_id = data['camper_id'],
            activity_id=data['activity_id'],
            time=data['time']
        )
        db.session.add(signup)
        db.session.commit()
        return make_response(signup.to_dict()),201
    except Exception as e:
        return make_response({"errors":["validation errors"]}),400
if __name__ == '__main__':
    app.run(port=5555, debug=True)

