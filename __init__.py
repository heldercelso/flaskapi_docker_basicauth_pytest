from .app import Users, Owners, Owner, Vehicles, Vehicle
from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy


def create_app(db_location):
    """
    Function that creates our Flask application.
    This function creates the Flask app, Flask-Restful API,
    and Flask-SQLAlchemy connection
    :param db_location: Connection string to the database
    :return: Initialized Flask app
    """

    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = db_location
    db = SQLAlchemy()

    db.init_app(app)

    api = Api(app)
    api.add_resource(Users, '/api/users')
    api.add_resource(Owners, '/api/customers')
    api.add_resource(Owner, '/api/customer/<doc>')
    api.add_resource(Vehicles, '/api/cars')
    api.add_resource(Vehicle, '/api/car/<doc>', '/api/car/<doc>/<pk>')
    return app