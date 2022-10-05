import pytest
from .tests.factories import CustomerFactory, CarFactory
from . import create_app

@pytest.fixture()
def client():
    app = create_app('sqlite:///pytest.db')
    app.config.update({
        "TESTING": True,
    })

    return app.test_client()

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def customer():
    return CustomerFactory()

@pytest.fixture
def car():
    return CarFactory()