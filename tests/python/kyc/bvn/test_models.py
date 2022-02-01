from datetime import datetime

import factory
from django.test import TestCase

from kyc.bvn.constants import PROVIDER_MY_IDENTITY_PASS
from kyc.bvn.models import BVNVerification
from tests.python.client.test_models import ClientFactory


class BVNVerificationFactory(factory.django.DjangoModelFactory):
    client = factory.SubFactory(ClientFactory)
    provider = PROVIDER_MY_IDENTITY_PASS
    bvn = '12345678900'
    first_name = 'John'
    last_name = 'Doe'
    phone_number = '+2347012345678'
    date_of_birth = datetime.now()

    class Meta:
        model = BVNVerification


class BVNVerificationModelTests(TestCase):
    def setUp(self):
        self.bvn_verification = BVNVerificationFactory.create()

    def test__str__(self):
        self.assertEqual(
            str(self.bvn_verification),
            f'BVNVerification: {self.bvn_verification.id}: 12345678900 - My Awesome Client - '
            f'{self.bvn_verification.datetime_created}',
        )
