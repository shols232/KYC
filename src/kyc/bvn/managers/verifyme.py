from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

import phonenumbers
from rest_framework import status

from kyc.bvn.constants import PROVIDER_VERIFY_ME
from kyc.bvn.models import BVNVerification
from kyc.bvn.providers.nigeria_verifyme.constants import VERIFY_ME_DATE_FORMAT
from kyc.bvn.providers.nigeria_verifyme.utils import VerifyMeRequestClient
from kyc.constants import CUSTOM_ERROR_STATUS_CODE

from .base import BaseBVNVerificationManager


class VerifyMeManager(BaseBVNVerificationManager):
    def get_bvn_verification_object_from_api(self, value: str, user_data: dict[str, Any]) -> Optional[BVNVerification]:
        """Return BVNVerification object created using response data from VerifyMe API."""

        verifyme_client = VerifyMeRequestClient(self.partner)
        response_data = verifyme_client.run(user_data)
        response_code = verifyme_client.response_code
        bvn_verification_object = None

        # handle timeout / 500 from provider
        if response_code == CUSTOM_ERROR_STATUS_CODE or status.is_server_error(response_code):
            self.errors = ['We are unable to validate your BVN at this time.']
            self.provider_failure = True
            return bvn_verification_object

        # handle invalid bvn
        if status.is_client_error(response_code):
            if 'code' in response_data and response_data['code'].lower() == 'access_denied_error':
                self.errors = ['We are unable to validate your BVN at this time.']
                self.provider_failure = True
            if 'message' in response_data:
                self.errors = [response_data['message']]
            else:
                self.errors = ['We are unable to validate your BVN at this time.']
                self.provider_failure = True

        # verifyme documentation had 200 but the API returns 201 so let's just support both
        elif response_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]:
            bvn_details = response_data['data']
            try:
                formatted_phone_number = phonenumbers.format_number(
                    phonenumbers.parse(bvn_details['phone'], 'NG'),
                    phonenumbers.PhoneNumberFormat.E164,
                )
            except (phonenumbers.NumberParseException, KeyError):
                formatted_phone_number = ''
            bvn_verification_object = BVNVerification.objects.create(
                bvn=value,
                partner=self.partner,
                provider=PROVIDER_VERIFY_ME,
                first_name=bvn_details['firstname'],
                last_name=bvn_details['lastname'],
                date_of_birth=datetime.strptime(bvn_details['birthdate'], VERIFY_ME_DATE_FORMAT).date(),
                phone_number=formatted_phone_number,
            )
            bvn_verification_object.api_responses.add(verifyme_client.api_response_object)

        return bvn_verification_object
