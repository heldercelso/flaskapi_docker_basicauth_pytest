from flask import Flask, Blueprint, request, jsonify, make_response, url_for, abort, g
from flask_restful import Resource, Api, marshal_with, fields, marshal
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound
import enum

from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()
from passlib.apps import custom_app_context as pwd_context


app = Flask(__name__)
api_bp = Blueprint('api_bp', __name__)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECURITY_UNAUTHORIZED_VIEW'] = None
db = SQLAlchemy(app)


class LimitException(Exception):
    def __init__(self, message):
        super().__init__(message)
class MissException(Exception):
    def __init__(self, message):
        super().__init__(message)
class ForbiddenException(Exception):
    def __init__(self, message):
        super().__init__(message)

@app.errorhandler(LimitException)
def db_limit_err_handler(e):
    return jsonify({'message': str(e)}), 403

@app.errorhandler(MissException)
def db_miss_err_handler(e):
    return jsonify({'message': str(e)}), 403

@app.errorhandler(ForbiddenException)
def db_forb_err_handler(e):
    return jsonify({'message': str(e)}), 403

@app.errorhandler(NoResultFound)
def db_not_found_err_handler(e):
    return jsonify({'message': str(e)}), 404

@app.errorhandler
def default_err_handler(e):
    return jsonify({'message': 'An unhandled exception occurred.'}), 500


userFields = {
    'id': fields.Integer,
    'username': fields.String,
}

customerFields = {
    'id': fields.Integer,
    'doc': fields.String,
    'name': fields.String,
    'sale_opp': fields.Boolean,
}

carFields = {
    'id': fields.Integer,
    'customer_doc': fields.String,
    'color': fields.String,
    'model': fields.String,
}


class CarColorsEnum(enum.Enum):
    yellow = 'yellow'
    blue = 'blue'
    gray = 'gray'

class CarModelsEnum(enum.Enum):
    hatch = 'hatch'
    sedan = 'sedan'
    convertible = 'convertible'


class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(32), index = True)
    password_hash = db.Column(db.String(128))
    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)
    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username = username).first()
    if not user or not user.verify_password(password):
        return False
    g.user = user
    return True


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doc = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    sale_opp = db.Column(db.Boolean, default=True)
    cars = db.relationship('Car', cascade='all,delete', backref='customer')

    def __repr__(self):
        return self.name

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_doc = db.Column(db.String, db.ForeignKey('customer.doc'), nullable=False)
    color = db.Column(db.Enum(CarColorsEnum), nullable=False)
    model = db.Column(db.Enum(CarModelsEnum), nullable=False)

    def __repr__(self):
        return self.customer_doc


class Users(Resource):
    @auth.login_required
    def get(self):
        users = User.query.all()
        return marshal(users, userFields)

    def post(self):
        data = request.json
        username = data['username']
        password = data['password']
        if not username or not password:
            #abort(400) # missing arguments
            raise MissException("Missing arguments.")
        user = User.query.filter_by(username=username)
        if user.first():
            #abort(400) # existing user
            raise LimitException("User already exist.")
        new_user = User(username=username)
        new_user.hash_password(password)
        db.session.add(new_user)
        db.session.commit()
        return marshal(user.first(), userFields), 201


class Owners(Resource):
    @auth.login_required
    def get(self):
        customers = Customer.query.all()
        return marshal(customers, customerFields)

    @auth.login_required
    def post(self):
        data = request.json
        customer = Customer(doc=data['doc'], name=data['name'])
        db.session.add(customer)
        db.session.commit()
        customers = Customer.query.all()
        return marshal(customers, customerFields), 201

class Owner(Resource):
    @auth.login_required
    def get(self, doc):
        customer = Customer.query.filter_by(doc=doc).first()
        if customer:
            return marshal(customer, customerFields)
        else:
            raise NoResultFound("Customer not found: " + doc)

    @auth.login_required
    def delete(self, doc):
        customer = Customer.query.filter_by(doc=doc).first()
        if customer:
            db.session.delete(customer)
            db.session.commit()
            customers = Customer.query.all()
            return marshal(customers, customerFields)
        else:
            raise NoResultFound("Customer not found: " + doc)

    @auth.login_required
    def put(self, doc):
        data = request.json
        customer = Customer.query.filter_by(doc=doc).first()
        if customer:
            customer.name = data['name']
            customer.doc = data['doc']
            db.session.commit()
            return marshal(customer, customerFields)
        else:
            raise NoResultFound("Customer not found: " + doc)


class Vehicles(Resource):
    @auth.login_required
    def get(self):
        cars = Car.query.all()
        return marshal(cars, carFields)

    @auth.login_required
    def post(self):
        data = request.json
        customer = Customer.query.filter_by(doc=data['customer_doc']).first()

        if customer:
            customer_cars = Car.query.filter_by(customer_doc=data['customer_doc'])

            if customer_cars.count() < 3:
                if data['color'] in set(item.value for item in CarColorsEnum) \
                   and data['model'] in set(item.value for item in CarModelsEnum):
                    car = Car(customer_doc=data['customer_doc'], color=data['color'], model=data['model'])
                    db.session.add(car)
                    customer.sale_opp = False
                    db.session.commit()
                    return marshal(customer_cars.all(), carFields), 201
                else:
                    raise MissException("Wrong car color (" + data['color'] +" not in 'yellow', 'blue' or 'gray') " + \
                                       "or model (" + data['model'] + " not in 'hatch', 'sedan' or 'convertible').")
            else:
                raise LimitException("Limit of cars reached (3) to the customer " + data['customer_doc'])
        else:
            raise NoResultFound("Customer not found: " + data['customer_doc'])

class Vehicle(Resource):
    @auth.login_required
    def get(self, doc, pk=None):
        customer_cars = Car.query.filter_by(customer_doc=doc).all()
        if customer_cars:
            return marshal(customer_cars, carFields)
        else:
            raise NoResultFound("The customer " + doc + " has no cars registered.")

    @auth.login_required
    def delete(self, doc, pk):
        car = Car.query.filter_by(id=pk, customer_doc=doc).first()
        if car:
            db.session.delete(car)
            customer_cars = Car.query.filter_by(customer_doc=doc)
            if customer_cars.count() == 0:
                customer = Customer.query.filter_by(doc=doc).first()
                if customer: customer.sale_opp = True
            db.session.commit()
            return marshal(customer_cars.all(), carFields)
        else:
            raise NoResultFound("Car not found for customer " + doc + " and pk " + pk)

    @auth.login_required
    def put(self, doc, pk):
        data = request.json
        car = Car.query.filter_by(id=pk, customer_doc=doc).first()
        if car:
            car.color=data['color']
            car.model=data['model']
            db.session.commit()
            return marshal(car, carFields)
        else:
            raise NoResultFound("Car not found for customer " + doc + " and pk " + pk)


api.add_resource(Users, '/api/users')
api.add_resource(Owners, '/api/customers')
api.add_resource(Owner, '/api/customer/<doc>')
api.add_resource(Vehicles, '/api/cars')
api.add_resource(Vehicle, '/api/car/<doc>', '/api/car/<doc>/<pk>')

app.register_blueprint(api_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)