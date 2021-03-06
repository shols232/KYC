import base64
import hashlib
import json
import uuid
from typing import Any, Tuple

import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from django.conf import settings
from django.utils import timezone
from requests import RequestException

from client.models import Client
from kyc.abstract import RequestClient
from kyc.constants import CUSTOM_ERROR_STATUS_CODE
from kyc.models import ClientProviderAPIKey
from lib.utils import log_api_response
from utilities.models import APIResponse

from ..nigeria_smile import constants


class SmileIdentityRequestClient(RequestClient):
    def __init__(self, client: Client) -> None:
        """Initialize request."""
        self.response_code = 0
        self.response_data: dict[str, Any] = {}
        self.client = client
        self.api_response_object: APIResponse = APIResponse()

    @staticmethod
    def __generate_secret_key(key: str) -> Tuple[str, float]:
        """Generate the secret key."""
        timestamp = timezone.now().timestamp()

        hashed = hashlib.sha256(f'{constants.SMILE_CLIENT_ID}:{timestamp}'.encode('utf-8')).hexdigest()
        public_key: RSAPublicKey = serialization.load_pem_public_key(
            base64.b64decode(str(key)), backend=default_backend()
        )

        cipher = public_key.encrypt(
            f'{constants.SMILE_CLIENT_ID}:{timestamp}'.encode('utf-8'),
            padding.PKCS1v15(),
        )
        encrypted = base64.b64encode(cipher)

        signature = f'{encrypted.decode("utf-8")}|{hashed}'
        return signature, timestamp

    def run(self, user_data: dict[str, Any], provider_name: str) -> dict[str, Any]:
        """Connect with smile identity api to return response."""

        api_key = ClientProviderAPIKey.objects.get(client=self.client, provider=provider_name).api_key
        secret_key, timestamp = self.__generate_secret_key(api_key)

        request_data = {
            'client_id': constants.SMILE_CLIENT_ID,
            'sec_key': secret_key,
            'timestamp': timestamp,
            'country': constants.SMILE_COUNTRY_CODE,
            'id_type': 'BVN',
            'id_number': user_data['bvn'],
            'first_name': user_data['first_name'],
            'last_name': user_data['last_name'],
            'dob': user_data['date_of_birth'],
            'client_params': {'job_id': str(uuid.uuid4()), 'user_id': user_data.get('id', '0'), 'job_type': 5},
        }

        phone_number = user_data.get('phone_number')
        if phone_number:
            request_data['phone_number'] = str(phone_number)

        try:
            response = requests.post(
                url=constants.SMILE_IDENTITY_API_URL,
                headers={'Content-Type': 'application/json'},
                data=json.dumps(request_data),
                timeout=settings.DEFAULT_REQUESTS_TIMEOUT,
            )
            self.response_code = response.status_code
            self.response_data = response.json()
            self.api_response_object = log_api_response(response)
        except RequestException as error:
            self.response_data = {'message': str(error)}
            self.response_code = error.response.status_code if error.response else CUSTOM_ERROR_STATUS_CODE

        return self.response_data
