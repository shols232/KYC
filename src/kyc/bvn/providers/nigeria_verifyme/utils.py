from __future__ import annotations

import json
from datetime import datetime
from typing import Any

import requests
from django.conf import settings
from requests.exceptions import RequestException

from client.models import Client
from kyc.abstract import RequestClient
from kyc.constants import CUSTOM_ERROR_STATUS_CODE
from lib.utils import get_api_settings, log_api_response
from utilities.models import APIResponse

from .constants import VERIFY_ME_BVN_URL, VERIFY_ME_DATE_FORMAT


class VerifyMeRequestClient(RequestClient):
    def __init__(self, partner: Client) -> None:
        """Initialize request."""
        self.response_code = 0
        self.response_data: dict[str, Any] = {}
        self.partner = partner
        self.api_response_object: APIResponse = (
            APIResponse()
        )  # mypy has an issue with this being optional because of log_api_response

    def run(self, user_data: dict[str, Any]) -> dict[str, Any]:
        """
        Verifyme to verify a user bvn.

        :param: user_data: dict containing the following
            bvn_value: the bvn of that user
            first_name: the first name of that user
            last_name: the last name of that user
            date_of_birth: the date of birth of the user formatted to string in %d-%m-%Y format
            phone_number: the phone number of the user
        :return: the response_data in dict
        """

        kyc_settings = get_api_settings(settings.PROVIDER_VERIFY_ME_NAME, self.partner)

        request_data = {
            'firstname': user_data['first_name'],
            'lastname': user_data['last_name'],
            'dob': datetime.strptime(user_data['date_of_birth'], '%Y-%m-%d').strftime(VERIFY_ME_DATE_FORMAT),
        }

        phone_number = user_data.get('phone_number')
        if phone_number:
            request_data['phone_number'] = phone_number

        try:
            response = requests.post(
                url=f'{VERIFY_ME_BVN_URL}/{user_data["bvn"]}',
                headers={
                    'Authorization': f'Bearer {kyc_settings["api_key"]}',
                    'Content-Type': 'application/json',
                },
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
