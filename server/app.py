#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import sqlalchemy
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


# ---PLANETS--- #

# GET /planets
@app.get('/planets')
def all_planets():
    planets = Planet.query.all()
    planet_dict = [ planet.to_dict(rules=("-missions",)) for planet in planets ]
    return jsonify( planet_dict ), 200

# GET /planets/:id
@app.get('/planets/<int:id>')
def planet_by_id(id):
    try:
        planet = Planet.query.filter(Planet.id == id).first()
        return jsonify( planet.to_dict() ), 200
    except AttributeError:
        return jsonify( {"error": "No planet found"} ), 404


# ---SCIENTISTS--- #

# GET /scientists
@app.get('/scientists')
def all_scientists():
    scientists = Scientist.query.all()
    scientist_dict = [ scientist.to_dict(rules=("-missions",)) for scientist in scientists ]
    return jsonify( scientist_dict ), 200

# GET /scientists/:id
@app.get('/scientists/<int:id>')
def scientist_by_id(id):
    try:
        scientist = Scientist.query.filter(Scientist.id == id).first()
        return jsonify( scientist.to_dict() ), 200
    except AttributeError:
        return jsonify( {"error": "No scientist found"} ), 404

# POST /scientists
@app.post('/scientists')
def create_scientist():
    data = request.json
    print(data)
    try:
        # scientist = Scientist(**data)
        scientist = Scientist(name=data["name"], field_of_study=data["field_of_study"])
        db.session.add( scientist )
        db.session.commit()
        return jsonify( scientist.to_dict() ), 201
    except:
        return { "error": "Not acceptable", "img": "https://httpstatusdogs.com/img/406.jpg" }, 406


# PATCH /scientists/:id
@app.patch('/scientists/<int:id>')
def update_scientist(id):
    try:
        data = request.json
        Scientist.query.filter( Scientist.id == id ).update( data )
        db.session.commit()

        scientist = Scientist.query.filter(Scientist.id == id).first()
        return jsonify( scientist.to_dict() ), 202
    except sqlalchemy.exc.IntegrityError as e:
        return jsonify( {"error": "Invalid data", "error_message": str(e)} ), 406


# DELETE /scientists/:id
@app.delete('/scientists/<int:id>')
def destroy_scientist(id):
    try:
        scientist = Scientist.query.filter(Scientist.id == id).first()
        db.session.delete( scientist )
        db.session.commit()
        return {}, 204
    except sqlalchemy.orm.exc.UnmappedInstanceError:
        return jsonify( {"error": "Not found" } ), 404


# ---MISSIONS--- #

# POST /missions
@app.post('/missions')
def create_mission():
    data = request.json
    planet = Planet.query.filter(Planet.id == data["planet_id"]).first()
    scientist = Scientist.query.filter(Scientist.id == data["scientist_id"]).first()
    mission = Mission(name=data["name"], scientist=scientist, planet=planet)
    db.session.add(mission)
    db.session.commit()

    return jsonify( mission.to_dict() ), 201


if __name__ == '__main__':
    app.run(port=5555, debug=True)
