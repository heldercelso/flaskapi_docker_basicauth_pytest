## INTRODUCTION

Flask API created to solve the following challenge:
```
To-Do List App
Description
Nork-Town is a weird place. Crows cawk the misty morning while old men squint. It’s a small
town, so the mayor had a bright idea to limit the number of cars a person may possess. One
person may have up to 3 vehicles. The vehicle, registered to a person, may have one color,
‘yellow’, ‘blue’ or ‘gray’. And one of three models, ‘hatch’, ‘sedan’ or ‘convertible’.
Carford car shop want a system where they can add car owners and cars. Car owners may
not have cars yet, they need to be marked as a sale opportunity. Cars cannot exist in the
system without owners.

Requirements

* Setup the dev environment with docker
* Using docker-compose with as many volumes as it takes
* Use Python’s Flask framework and any other library
* Use any SQL database
* Secure routes
* Write tests
```

## INITIALIZATION
```
$ docker-compose build
$ docker-compose up
```

Endpoints:
- `127.0.0.1:5000/api/users`
- `127.0.0.1:5000/api/customers`
- `127.0.0.1:5000/api/customer/<doc>`
- `127.0.0.1:5000/api/cars`
- `127.0.0.1:5000/api/car/<doc>`
- `127.0.0.1:5000/api/car/<doc>/<pk>`


### ENDPOINT USERS

* Getting all users:

    `GET 127.0.0.1:5000/api/users`

    Curl command:

    `$ curl -u testuser:testpass -X GET http://127.0.0.1:5000/api/users`

* Adding an user:

    `POST 127.0.0.1:5000/api/users`

    Curl command:

    `$ curl -i -X POST -H "Content-Type: application/json" -d '{"username": "testuser", "password": "testpass"}' http://127.0.0.1:5000/api/users`


### ENDPOINT CUSTOMERS

* Getting all customers:

    `GET 127.0.0.1:5000/api/customers`

    Curl command:

    `$ curl -u testuser:testpass -X GET http://127.0.0.1:5000/api/customers`

* Adding a customer:

    `POST 127.0.0.1:5000/api/customers`

    Curl command:

    `$ curl -u testuser:testpass -i -X POST -H "Content-Type: application/json" -d '{"doc": "399789456321", "name": "Helder"}' http://127.0.0.1:5000/api/customers`

* Getting customer by document:

    `GET 127.0.0.1:5000/api/customer/<doc>`

    Curl command:

    `$ curl -u testuser:testpass -X GET http://127.0.0.1:5000/api/customer/399789456321`

* Updating customer by document:

    `PUT 127.0.0.1:5000/api/customer/<doc>`

    Curl command:

    `$ curl -u testuser:testpass -i -X PUT -H "Content-Type: application/json" -d '{"doc": "399789456322", "name": "Helder"}' http://127.0.0.1:5000/api/customer/399789456321`

* Deleting customer by document:

    `DEL 127.0.0.1:5000/api/customer/<doc>`

    Curl command:

    `$ curl -u testuser:testpass -X DELETE http://127.0.0.1:5000/api/customer/399789456321`


### ENDPOINT CARS

* Getting all cars:

    `GET 127.0.0.1:5000/api/cars` - Retorna todos carros

    Curl command:

    `$ curl -u testuser:testpass -X GET http://127.0.0.1:5000/api/cars`

* Adding a car:

    `POST 127.0.0.1:5000/api/cars` - Adiciona carro

    Curl command:

    `$ curl -u testuser:testpass -i -X POST -H "Content-Type: application/json" -d '{"customer_doc": "399789456321", "color": "yellow", "model": "sedan"}' http://127.0.0.1:5000/api/cars`

* Getting all cars of a customer by document:

    `GET 127.0.0.1:5000/api/car/<doc>`

    Curl command:

    `$ curl -u testuser:testpass -X GET http://127.0.0.1:5000/api/car/399789456321`

* Updating a car by pk and customer document:

    `PUT 127.0.0.1:5000/api/car/<doc>/<pk>`

    Curl command:

    `$ curl -u testuser:testpass -i -X PUT -H "Content-Type: application/json" -d '{"customer_doc": "399789456321", "color": "blue", "model": "sedan"}' http://127.0.0.1:5000/api/car/399789456321/1`

* Deleting a car by pk and customer document:

    `DEL 127.0.0.1:5000/api/car/<doc>/<pk>`

    Curl command:

    `$ curl -u testuser:testpass -X DELETE http://127.0.0.1:5000/api/car/399789456321/1`

## PYTEST

To run with docker from the application itself:

```
$ docker-compose up
$ docker exec -ti flask_app pytest -vx
```

To run outside of docker:

```
$ python -m venv venv
$ source venv/Scripts/activate
$ pip install requirements.txt
$ pytest -vx
```

## DATABASE

The database for the API (`todo.db`) is separate from the database for tests (`pytest.db`). Both are already populated with the user `testuser/testpass`.
In addition there is a backup: `db_bk.db`.

To create an empty database, use:

```
$ source venv/Scripts/activate
$ python
$ from app import db
$ db.create_all()
```

## STRUCTURE

```
.
└── flask_api
   ├── tests
   │   ├── base.py
   │   ├── factories.py
   │   └── test_models.py
   ├── .gitignore
   ├── app.py
   ├── conftest.py
   ├── db_bk.db
   ├── docker-compose.yaml
   ├── Dockerfile
   ├── pytest.db
   ├── pytest.ini
   ├── README.md
   ├── requirements.txt
   ├── todo.db
   └── pytest.ini
```