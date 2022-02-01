import factory
from django.test import TestCase

from client.models import Client, ClientApiKey


class ClientFactory(factory.django.DjangoModelFactory):
    name = 'My Awesome Client'
    email = 'my@awesome.client'
    domain = 'awesome.client'

    class Meta:
        model = Client
        django_get_or_create = (
            'name',
            'email',
        )


class ClientApiKeyFactory(factory.django.DjangoModelFactory):
    client = factory.SubFactory(ClientFactory)
    api_key = 'some_api_key'

    class Meta:
        model = ClientApiKey
        django_get_or_create = ('client', 'api_key')


class ClientModelTests(TestCase):
    def setUp(self):
        self.client = ClientFactory.create(name='Client1')

    def test__str__(self):
        self.assertEqual(str(self.client), 'Client: Client1')


class CLientApiKeyModelTests(TestCase):
    def setUp(self):
        self.client_api_key = ClientApiKeyFactory.create()

    def test__str__(self):
        self.assertEqual(str(self.client_api_key), 'ClientApiKey: My Awesome Client')
