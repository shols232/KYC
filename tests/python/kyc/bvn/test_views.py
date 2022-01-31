import json
from datetime import datetime
from django.test import TestCase

import mock
import responses
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from kyc.bvn.constants import (
    PROVIDER_MY_IDENTITY_PASS,
)
from kyc.bvn.models import BVNVerification
from kyc.bvn.providers.nigeria_my_identity_pass.constants import MY_IDENTITY_PAY_BVN_URL
from tests.python.client.test_models import ClientFactory
from tests.python.kyc.bvn.test_models import BVNVerificationFactory
from tests.python.testutils import TestUtils


class ValidateBVNViewTests(APITestCase):
    def setUp(self) -> None:
        self.client = ClientFactory(name='Client', domain='domain.ng', email='cliet@domain.com')


    def mock_failed_my_identity_pass_call(self):
        """Mock a failed API call to MyIdentityPass. This ensures a provider failure occurs."""
        responses.add(
            responses.POST, url=MY_IDENTITY_PAY_BVN_URL, json={}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    @responses.activate
    def test_validate_bvn__my_identity_pass_success(self):
        """Test bvn validation via MyIdentityPass."""

        self.assertEqual(BVNVerification.objects.count(), 0)

        self.mock_failed_verify_me_api_call()
        self.mock_failed_smile_identity_api_call()
        responses.add(
            responses.POST,
            url=MY_IDENTITY_PAY_BVN_URL,
            json={
                'status': True,
                'detail': 'Verification Successful',
                'response_code': '00',
                'bvn_data': {
                    'bvn': '12345678909',
                    'firstName': 'JOHN',
                    'middleName': 'LOREN',
                    'lastName': 'DOE',
                    'dateOfBirth': '01-Sep-1990',
                    'registrationDate': '24-Feb-2016',
                    'enrollmentBank': '033',
                    'enrollmentBranch': 'ADDRESS, PLACE',
                    'email': '',
                    'gender': 'Male',
                    'levelOfAccount': '',
                    'lgaOfOrigin': 'LGA',
                    'lgaOfResidence': 'LGA',
                    'maritalStatus': 'Single',
                    'nin': '',
                    'nameOnCard': 'JOHN DOE LOREN',
                    'nationality': 'Nigeria',
                    'phoneNumber1': '08012345678',
                    'phoneNumber2': '',
                    'residentialAddress': '1 ADDRESS STREET, CITY,',
                    'stateOfOrigin': 'Lagos State',
                    'stateOfResidence': 'Lagos State',
                    'title': 'Mr',
                    'watchListed': 'NO',
                    'base64Image': 'some_image_code',
                },
            },
            status=status.HTTP_200_OK,
        )

        response = self.client.post(
            path=reverse('kyc_api:bvn_api_v1:validate_bvn'),
            data={
                'bvn': 12345678901,
                'first_name': 'John',
                'last_name': 'Doe',
                'phone_number': '+2348012345678',
                'date_of_birth': '1990-09-01',
            },
            **TestUtils.generate_client_auth_headers(self.client),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(
            response.json(),
            {
                'is_valid': True,
                'provider': 'my_identity_pass',
                'errors': {
                    'verify_me': ['We are unable to validate your BVN at this time.'],
                    'smile_identity': ['We are unable to validate your BVN at this time.'],
                },
                'providers_attempted': ['verify_me', 'smile_identity', 'my_identity_pass'],
            },
        )
        self.assertEqual(BVNVerification.objects.count(), 1)
        bvn_verification_object = BVNVerification.objects.first()
        self.assertEqual(bvn_verification_object.first_name, 'JOHN')
        self.assertEqual(bvn_verification_object.last_name, 'DOE')
        self.assertEqual(bvn_verification_object.phone_number, '+2348012345678')
        self.assertEqual(bvn_verification_object.date_of_birth.strftime('%Y-%m-%d'), '1990-09-01')
        self.assertEqual(bvn_verification_object.provider, PROVIDER_MY_IDENTITY_PASS)
        self.assertEqual(bvn_verification_object.client, self.client)
        self.assertEqual(len(responses.calls), 3)
        self.assertDictEqual(
            json.loads(bvn_verification_object.api_responses.order_by('-datetime_created').first().response),
            json.loads(responses.calls[2].response.text),
        )

    @responses.activate
    def test_validate_bvn__my_identity_pass_bvn_not_found(self):
        """Test BVN not found in MyIdentityPass."""
        self.assertEqual(BVNVerification.objects.count(), 0)

        responses.add(
            responses.POST,
            url=MY_IDENTITY_PAY_BVN_URL,
            json={'status': False, 'response_code': '01', 'message': 'BVN not found'},
            status=status.HTTP_200_OK,
        )

        response = self.client.post(
            path=reverse('kyc_api:bvn_api_v1:validate_bvn'),
            data={
                'bvn': 12345678901,
                'first_name': 'John',
                'last_name': 'Doe',
                'phone_number': '+2348012345678',
                'date_of_birth': '1990-09-01',
            },
            **TestUtils.generate_client_auth_headers(self.client),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(
            response.json(),
            {
                'is_valid': False,
                'provider': 'my_identity_pass',
                'providers_attempted': ['verify_me', 'smile_identity', 'my_identity_pass'],
                'errors': {
                    'verify_me': ['We are unable to validate your BVN at this time.'],
                    'smile_identity': ['We are unable to validate your BVN at this time.'],
                    'my_identity_pass': ['BVN not found'],
                },
            },
        )
        self.assertEqual(BVNVerification.objects.count(), 0)
        self.assertEqual(len(responses.calls), 3)

    @responses.activate
    def test_validate_bvn__my_identity_pass_invalid_bvn(self):
        """Test invalid BVN in MyIdentityPass."""
        self.assertEqual(BVNVerification.objects.count(), 0)

        self.mock_failed_verify_me_api_call()
        self.mock_failed_smile_identity_api_call()
        responses.add(
            responses.POST,
            url=MY_IDENTITY_PAY_BVN_URL,
            json={
                'status': False,
                'response_code': '01',
            },
            status=status.HTTP_200_OK,
        )

        response = self.client.post(
            path=reverse('kyc_api:bvn_api_v1:validate_bvn'),
            data={
                'bvn': 12345678901,
                'first_name': 'John',
                'last_name': 'Doe',
                'phone_number': '+2348012345678',
                'date_of_birth': '1990-09-01',
            },
            **TestUtils.generate_client_auth_headers(self.client),
        )

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertDictEqual(
            response.json(),
            {
                'providers_attempted': ['verify_me', 'smile_identity', 'my_identity_pass'],
                'errors': {
                    'verify_me': ['We are unable to validate your BVN at this time.'],
                    'smile_identity': ['We are unable to validate your BVN at this time.'],
                    'my_identity_pass': ['We are unable to validate your BVN at this time.'],
                },
            },
        )
        self.assertEqual(BVNVerification.objects.count(), 0)
        self.assertEqual(len(responses.calls), 3)

    @responses.activate
    def test_validate_bvn__my_identity_pass_details_not_matching(self):
        """Test BVN details not matching in MyIdentityPass."""
        self.assertEqual(BVNVerification.objects.count(), 0)

        self.mock_failed_verify_me_api_call()
        self.mock_failed_smile_identity_api_call()
        responses.add(
            responses.POST,
            url=MY_IDENTITY_PAY_BVN_URL,
            json={
                'status': True,
                'detail': 'Verification Successful',
                'response_code': '00',
                'bvn_data': {
                    'bvn': '12345678901',
                    'firstName': 'OTHER',
                    'middleName': 'LOREN',
                    'lastName': 'PERSON',
                    'dateOfBirth': '01-Sep-1991',
                    'registrationDate': '24-Feb-2016',
                    'enrollmentBank': '033',
                    'enrollmentBranch': 'ADDRESS, PLACE',
                    'email': '',
                    'gender': 'Male',
                    'levelOfAccount': '',
                    'lgaOfOrigin': 'LGA',
                    'lgaOfResidence': 'LGA',
                    'maritalStatus': 'Single',
                    'nin': '',
                    'nameOnCard': 'OTHER PERSON LOREN',
                    'nationality': 'Nigeria',
                    'phoneNumber1': '',
                    'phoneNumber2': '08022222222',
                    'residentialAddress': '1 ADDRESS STREET, CITY,',
                    'stateOfOrigin': 'Lagos State',
                    'stateOfResidence': 'Lagos State',
                    'title': 'Mr',
                    'watchListed': 'NO',
                    'base64Image': 'some_image_code',
                },
            },
            status=status.HTTP_200_OK,
        )

        response = self.client.post(
            path=reverse('kyc_api:bvn_api_v1:validate_bvn'),
            data={
                'bvn': 12345678901,
                'first_name': 'John',
                'last_name': 'Doe',
                'phone_number': '+2348012345678',
                'date_of_birth': '1990-09-01',
            },
            **TestUtils.generate_client_auth_headers(self.client),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(
            response.json(),
            {
                'is_valid': False,
                'provider': 'my_identity_pass',
                'providers_attempted': ['verify_me', 'smile_identity', 'my_identity_pass'],
                'errors': {
                    'verify_me': ['We are unable to validate your BVN at this time.'],
                    'smile_identity': ['We are unable to validate your BVN at this time.'],
                    'my_identity_pass': [
                        'First name does not match.',
                        'Last name does not match.',
                        'Date of birth does not match.',
                        'Phone number does not match.',
                    ],
                },
            },
        )
        self.assertEqual(BVNVerification.objects.count(), 1)
        bvn_verification_object = BVNVerification.objects.first()
        self.assertEqual(bvn_verification_object.first_name, 'OTHER')
        self.assertEqual(bvn_verification_object.last_name, 'PERSON')
        self.assertEqual(bvn_verification_object.phone_number, '')
        self.assertEqual(bvn_verification_object.date_of_birth.strftime('%Y-%m-%d'), '1991-09-01')
        self.assertEqual(bvn_verification_object.provider, PROVIDER_MY_IDENTITY_PASS)
        self.assertEqual(bvn_verification_object.client, self.client)
        self.assertEqual(len(responses.calls), 3)
        self.assertDictEqual(
            json.loads(bvn_verification_object.api_responses.order_by('-datetime_created').first().response),
            json.loads(responses.calls[2].response.text),
        )

    @responses.activate
    def test_cache_validation_success(self):
        """Test an already saved BVN verification with success."""
        BVNVerificationFactory.create(
            date_of_birth=datetime.strptime('2021-09-09', '%Y-%m-%d'),
            first_name='John',
            last_name='Doe',
            phone_number='+2348012345678',
            bvn='12345678901',
            client=self.client,
            provider=PROVIDER_MY_IDENTITY_PASS,
        )

        self.assertEqual(BVNVerification.objects.count(), 1)

        response = self.client.post(
            path=reverse('kyc_api:bvn_api_v1:validate_bvn'),
            data={
                'bvn': 12345678901,
                'first_name': 'John',
                'last_name': 'Doe',
                'phone_number': '+2348012345678',
                'date_of_birth': '2021-09-09',
            },
            **TestUtils.generate_client_auth_headers(self.client),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(
            response.json(),
            {'is_valid': True, 'errors': {}, 'provider': 'verify_me', 'providers_attempted': ['verify_me']},
        )
        self.assertEqual(BVNVerification.objects.count(), 1)
        bvn_verification_object = BVNVerification.objects.first()
        self.assertEqual(bvn_verification_object.provider, PROVIDER_MY_IDENTITY_PASS)
        self.assertEqual(bvn_verification_object.client, self.client)
        self.assertEqual(len(responses.calls), 0)

    @responses.activate
    def test_cache_validation_failure(self):
        """Test an already saved BVN verification with failure."""
        BVNVerificationFactory.create(
            date_of_birth=datetime.strptime('2021-09-09', '%Y-%m-%d'),
            first_name='John',
            last_name='Doe',
            phone_number='+2348012345678',
            bvn='12345678901',
            client=self.client,
            provider=PROVIDER_MY_IDENTITY_PASS,
        )

        self.assertEqual(BVNVerification.objects.count(), 1)

        response = self.client.post(
            path=reverse('kyc_api:bvn_api_v1:validate_bvn'),
            data={
                'bvn': 12345678901,
                'first_name': 'Test',
                'last_name': 'Person',
                'phone_number': '+2341111111111',
                'date_of_birth': '1921-08-08',
            },
            **TestUtils.generate_client_auth_headers(self.client),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(
            response.json(),
            {
                'is_valid': False,
                'errors': {
                    'verify_me': [
                        'First name does not match.',
                        'Last name does not match.',
                        'Date of birth does not match.',
                        'Phone number does not match.',
                    ]
                },
                'provider': 'verify_me',
                'providers_attempted': ['verify_me'],
            },
        )
        self.assertEqual(BVNVerification.objects.count(), 1)
        bvn_verification_object = BVNVerification.objects.first()
        self.assertEqual(bvn_verification_object.provider, PROVIDER_MY_IDENTITY_PASS)
        self.assertEqual(bvn_verification_object.client, self.client)
        self.assertEqual(len(responses.calls), 0)