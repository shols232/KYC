from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Optional

import phonenumbers
from rest_framework import status

from kyc.bvn.constants import PROVIDER_SMILE_IDENTITY
from kyc.bvn.models import BVNVerification
from kyc.bvn.providers.nigeria_smile import constants
from kyc.bvn.providers.nigeria_smile.utils import SmileIdentityRequestClient

from .base import BaseBVNVerificationManager

LOGGER = logging.getLogger(__name__)


class SmileIdentityManager(BaseBVNVerificationManager):
    def _validate_actions_dob_match(self, actions: dict[str, Any]) -> bool:
        """Validate the actions dob from the response data."""
        return actions['Verify_ID_Number'].lower() == 'verified' and actions['DOB'].lower() in [
            constants.SMILE_BVN_STATUS_EXACT_MATCH,
            constants.SMILE_BVN_STATUS_PARTIAL_MATCH,
            constants.SMILE_BVN_STATUS_TRANSPOSED_MATCH,
        ]

    def _validate_actions_phone_match(self, actions: dict[str, Any]) -> bool:
        """Validate the actions phone from the response data."""
        return actions['Phone_Number'].lower() == constants.SMILE_BVN_STATUS_EXACT_MATCH

    def _validate_actions_name_match(self, actions: dict[str, Any]) -> bool:
        """Validate the actions name from the response data."""
        return actions['Names'].lower() in [
            constants.SMILE_BVN_STATUS_EXACT_MATCH,
            constants.SMILE_BVN_STATUS_PARTIAL_MATCH,
            constants.SMILE_BVN_STATUS_TRANSPOSED_MATCH,
        ]

    def get_bvn_verification_object_from_api(self, value: str, user_data: dict[str, Any]) -> Optional[BVNVerification]:
        """Return BVNVerification object created using response data from SmileIdentity API."""
        client = SmileIdentityRequestClient(self.partner)
        response_data = client.run(user_data)
        status_code = client.response_code
        bvn_verification_object = None

        # handle timeout / 500 from provider
        if status_code != status.HTTP_200_OK:
            self.errors = ['We are unable to validate your BVN at this time.']
            self.provider_failure = True
            return bvn_verification_object

        if str(response_data['ResultCode']) in constants.SMILE_BVN_RESULT_CODE_INVALID_ID:
            self.errors = ['Invalid BVN. Please ensure you have entered the number correctly.']
            return bvn_verification_object

        # handle a 200 response but failure on the provider system
        if str(response_data['ResultCode']) not in constants.SMILE_BVN_RESULT_CODE_VALID:
            self.errors = ['We are unable to validate your BVN at this time.']
            self.provider_failure = True
            return bvn_verification_object

        try:
            dob_match = self._validate_actions_dob_match(response_data['Actions'])
            name_match = self._validate_actions_name_match(response_data['Actions'])
            phone_number_match = self._validate_actions_phone_match(response_data['Actions'])
            phone_number = user_data.get('phone_number')
            if phone_number:
                try:
                    formatted_phone_number = phonenumbers.format_number(
                        phonenumbers.parse(phone_number, 'NG'),
                        phonenumbers.PhoneNumberFormat.E164,
                    )
                except (phonenumbers.NumberParseException, KeyError):
                    formatted_phone_number = ''
            date_of_birth = datetime.strptime(user_data['date_of_birth'], '%Y-%m-%d')

            if dob_match and name_match and phone_number_match:
                bvn_verification_object = BVNVerification.objects.create(
                    bvn=user_data['bvn'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    phone_number=formatted_phone_number,
                    date_of_birth=date_of_birth,
                    provider=PROVIDER_SMILE_IDENTITY,
                    partner=self.partner,
                )
                bvn_verification_object.api_responses.add(client.api_response_object)

            else:
                # If values don't match, use wrong data so the validator will show errors.
                # BVNVerification object is not saved since the data is wrong data.
                wrong_date = datetime.today() + timedelta(days=2)
                bvn_verification_object = BVNVerification(
                    bvn=value,
                    first_name=user_data['first_name'] if name_match else '#################',
                    last_name=user_data['last_name'] if name_match else '################',
                    date_of_birth=date_of_birth if dob_match else wrong_date,
                    phone_number=formatted_phone_number if phone_number_match else '',
                    partner=self.partner,
                    provider=PROVIDER_SMILE_IDENTITY,
                )
        except KeyError:
            LOGGER.exception(
                'kyc::bvn::validators::smile_identity::Validator::validate_api::Key error when user bvn validation',
                extra={'user_data': user_data},
            )
            self.errors = ['We are unable to validate your BVN at this time.']
            self.provider_failure = True

        return bvn_verification_object
