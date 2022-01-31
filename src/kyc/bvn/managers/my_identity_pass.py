from __future__ import annotations

import logging
from typing import Any, Optional

import phonenumbers
from dateutil import parser
from django.utils import timezone
from rest_framework import status

from kyc.bvn.constants import PROVIDER_MY_IDENTITY_PASS
from kyc.bvn.models import BVNVerification
from kyc.bvn.providers.nigeria_my_identity_pass.constants import (
    MY_IDENTITY_PAY_SUCCESS_RESPONSE_CODE,
)
from kyc.bvn.providers.nigeria_my_identity_pass.utils import MyIdentityPassRequestClient
from lib.utils import ParseYearLastCentury

from .base import BaseBVNVerificationManager

LOGGER = logging.getLogger(__name__)


class MyIdentityPassManager(BaseBVNVerificationManager):
    def get_bvn_verification_object_from_api(self, value: str, user_data: dict[str, Any]) -> Optional[BVNVerification]:
        """Return BVNVerification object created using response data from MyIdentityPass API."""

        bvn_verification_object = None

        client = MyIdentityPassRequestClient(self.client)
        response_data = client.run(user_data)
        status_code = client.status_code

        response_status = response_data.get('status')
        response_code = response_data.get('response_code', '')

        # MyIdentityPass returns a '00' response code, status of True and status code of 200 if it's successfull
        if (
            status_code == status.HTTP_200_OK
            and response_code == MY_IDENTITY_PAY_SUCCESS_RESPONSE_CODE
            and response_status
        ):
            try:
                bvn_first_name = response_data['bvn_data']['firstName']
                bvn_last_name = response_data['bvn_data']['lastName']
                bvn_phone_number = response_data['bvn_data']['phoneNumber1']
                date_of_birth = parser.parse(timestr=response_data['bvn_data']['dateOfBirth'], dayfirst=True).date()

                if date_of_birth >= timezone.now().date():
                    date_of_birth = parser.parse(
                        timestr=response_data['bvn_data']['dateOfBirth'],
                        parserinfo=ParseYearLastCentury(),
                        dayfirst=True,
                    ).date()

                try:
                    formatted_phone_number = phonenumbers.format_number(
                        phonenumbers.parse(bvn_phone_number, 'NG'),
                        phonenumbers.PhoneNumberFormat.E164,
                    )
                except phonenumbers.NumberParseException:
                    formatted_phone_number = ''

                bvn_verification_object = BVNVerification.objects.create(
                    bvn=user_data['bvn'],
                    first_name=bvn_first_name,
                    last_name=bvn_last_name,
                    phone_number=formatted_phone_number,
                    date_of_birth=date_of_birth,
                    client=self.client,
                    provider=PROVIDER_MY_IDENTITY_PASS,
                )
                bvn_verification_object.api_responses.add(client.api_response_object)
            except KeyError:
                self.provider_failure = True
        else:
            self.provider_failure = True

        return bvn_verification_object
