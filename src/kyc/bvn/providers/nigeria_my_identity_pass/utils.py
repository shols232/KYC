from __future__ import annotations

import json
from typing import Any

import requests
from django.conf import settings
from requests.exceptions import RequestException

from client.models import Client
from kyc.abstract import RequestClient
from kyc.constants import CUSTOM_ERROR_STATUS_CODE
from kyc.models import ClientProviderAPIKey
from lib.utils import log_api_response
from utilities.models import APIResponse

from .constants import MY_IDENTITY_PAY_BVN_URL


class MyIdentityPassRequestClient(RequestClient):
    def __init__(self, client: Client) -> None:
        """Initialize request."""
        self.status_code = 0
        self.response_data: dict[str, Any] = {}
        self.client = client
        self.api_response_object: APIResponse = (
            APIResponse()
        )

    def run(self, user_data: dict[str, Any]) -> dict[str, Any]:
        """
        Myidentitypass to verify a user bvn.

        :param bvn_value: the bvn of that user
        :return: the response_data in dict
        """

        request_data = {
            'number': user_data['bvn'],
        }
        api_key = ClientProviderAPIKey.objects.get(client=self.client, provider=user_data['provider']).api_key

        try:
            response = requests.post(
                url=MY_IDENTITY_PAY_BVN_URL,
                headers={'x-api-key': api_key, 'Content-Type': 'application/json'},
                data=json.dumps(request_data),
                timeout=settings.DEFAULT_REQUESTS_TIMEOUT,
            )
            self.response_data = response.json()
            self.status_code = response.status_code
            self.api_response_object = log_api_response(response)
        except RequestException as error:
            self.response_data = {'message': str(error)}
            self.status_code = error.response.status_code if error.response else CUSTOM_ERROR_STATUS_CODE

        return self.response_data
