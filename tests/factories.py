# from products.tests.factories import ProductFactory
import factory
import factory.fuzzy

from ..app import Customer, Car

CARCOLOR_OPTIONS = ['yellow', 'blue', 'gray']
CARMODEL_OPTIONS = ['hatch', 'sedan', 'convertible']


class CustomerFactory(factory.Factory):
    doc = factory.Faker("cpf", locale="pt_BR")
    name = factory.Faker("first_name")
    sale_opp = True

    class Meta:
        model = Customer


class CarFactory(factory.Factory):
    customer_doc = factory.Faker("cpf", locale="pt_BR")
    color = factory.fuzzy.FuzzyChoice(choices=CARCOLOR_OPTIONS)
    model = factory.fuzzy.FuzzyChoice(choices=CARMODEL_OPTIONS)

    class Meta:
        model = Car