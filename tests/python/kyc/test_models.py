import factory

from kyc.models import ClientProviderAPIKey
from tests.python.client.test_models import ClientFactory

class ClientProviderApiKeyFactory(factory.django.DjangoModelFactory):
    client = factory.SubFactory(ClientFactory)
    provider = "MIP"
    api_key = 'some_api_key'

    class Meta:
        model = ClientProviderAPIKey
        django_get_or_create = ('client', 'api_key', 'provider')
