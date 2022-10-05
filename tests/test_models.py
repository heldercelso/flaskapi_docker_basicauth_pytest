import pytest

from ..app import Customer, Car
from click import echo
import json
from ..app import LimitException
from sqlalchemy.orm.exc import NoResultFound

from requests.auth import _basic_auth_str


#################################################################
######################## CLIENT TESTS ###########################
#################################################################


headers = {'Authorization': _basic_auth_str('testuser', 'testpass')}
class TestCustomerModel:
    def test___str__(self, customer):
        # test repr function declared on models
        assert customer.__repr__() == customer.name
        assert repr(customer) == customer.name

    def test_get_customers(self, client):
        with pytest.raises(NoResultFound) as exc_info:
            resp = client.get('/api/customer/39987456322', headers=headers)
        assert isinstance(exc_info.value, NoResultFound)
        resp = client.get('/api/users', headers=headers)
        assert resp.status_code == 200
        
        data = {'doc': '12345678939', 'name': 'Fulano', 'sale_opp': True}

        new_customer = Customer(doc=data['doc'], name=data['name'], sale_opp=data['sale_opp'])
        assert new_customer.name == 'Fulano'
        assert new_customer.doc == '12345678939'
        assert new_customer.sale_opp == True

    def test_post_customers(self, client):
        data = {'doc': '39987456321', 'name': 'Fulano', 'sale_opp': True}
        resp = client.post('/api/customers', headers=headers)
        assert resp.status_code == 400
        resp = client.post('/api/customers', data=json.dumps(data), content_type='application/json;', headers=headers)
        assert resp.status_code == 201
        
        
    def test_get_specific_customer(self, client):
        resp = client.get('/api/customer/39987456321', headers=headers)
        assert resp.status_code == 200
        assert resp.get_json()['name'] == 'Fulano'
        assert resp.get_json()['doc'] == '39987456321'
        assert resp.get_json()['sale_opp'] == True

    def test_update_specific_customer(self, client):
        data = {'doc': '39987456322', 'name': 'Ciclano'}
        resp = client.put('/api/customer/39987456321', data=json.dumps(data), content_type='application/json;', headers=headers)
        assert resp.status_code == 200
        assert resp.get_json()['name'] == 'Ciclano'
        assert resp.get_json()['doc'] == '39987456322'

    def test_delete_specific_customer(self, client):
        resp = client.delete('/api/customer/39987456322', headers=headers)
        assert resp.status_code == 200
        get_customer = Customer.query.filter_by(doc='39987456322').first()
        assert get_customer == None


#################################################################
########################## CAR TESTS ############################
#################################################################

class TestCarModel:
    def test___str__(self, car):
        # test repr function declared on models
        assert car.__repr__() == car.customer_doc
        assert repr(car) == car.customer_doc

    def test_get_cars(self, client):
        resp = client.get('/api/cars', headers=headers)
        assert resp.status_code == 200

    def test_post_cars(self, client):
        customer_data = {'doc': '39987456321', 'name': 'Fulano', 'sale_opp': True}
        client.post('/api/customers', data=json.dumps(customer_data), content_type='application/json;', headers=headers)

        get_customer = Customer.query.filter_by(doc='39987456321').first()
        assert get_customer.sale_opp == True

        data = {'customer_doc': '39987456321', 'color': 'yellow', 'model': 'hatch'}
        resp = client.post('/api/cars', headers=headers)
        assert resp.status_code == 400
        resp = client.post('/api/cars', data=json.dumps(data), content_type='application/json;', headers=headers)
        assert resp.status_code == 201
        
        get_customer = Customer.query.filter_by(doc='39987456321').first()
        assert get_customer.sale_opp == False

    def test_post_limit_three_cars(self, client):
        data = {'customer_doc': '39987456321', 'color': 'blue', 'model': 'hatch'}
        resp = client.post('/api/cars', data=json.dumps(data), content_type='application/json;', headers=headers)
        assert resp.status_code == 201
        
        data = {'customer_doc': '39987456321', 'color': 'blue', 'model': 'sedan'}
        resp = client.post('/api/cars', data=json.dumps(data), content_type='application/json;', headers=headers)
        assert resp.status_code == 201

        with pytest.raises(LimitException) as exc_info:
            data = {'customer_doc': '39987456321', 'color': 'gray', 'model': 'convertible'}
            resp = client.post('/api/cars', data=json.dumps(data), content_type='application/json;', headers=headers)
        assert isinstance(exc_info.value, LimitException)

    def test_get_customer_cars(self, client):
        resp = client.get('/api/car/39987456321', headers=headers)
        assert resp.status_code == 200
        assert resp.get_json()[0]['customer_doc'] == '39987456321'
        assert resp.get_json()[0]['color'] == 'CarColorsEnum.yellow'
        assert resp.get_json()[0]['model'] == 'CarModelsEnum.hatch'

    def test_update_specific_car(self, client):
        data = {'color': 'blue', 'model': 'sedan'}
        resp = client.put('/api/car/39987456321/1', data=json.dumps(data), content_type='application/json;', headers=headers)
        assert resp.status_code == 200
        assert resp.get_json()['color'] == 'CarColorsEnum.blue'
        assert resp.get_json()['model'] == 'CarModelsEnum.sedan'

    def test_delete_specific_car(self, client):
        resp = client.delete('/api/car/39987456321/1', headers=headers)
        assert resp.status_code == 200
        get_car = Car.query.filter_by(id=1).first()
        assert get_car == None

    def test_sale_opp_delete_cars(self, client):
        resp = client.delete('/api/car/39987456321/2', headers=headers)
        assert resp.status_code == 200
        
        resp = client.delete('/api/car/39987456321/3', headers=headers)
        assert resp.status_code == 200
        
        get_customer = Customer.query.filter_by(doc='39987456321').first()
        assert get_customer.sale_opp == True
        
        client.delete('/api/customer/39987456321', headers=headers)
        