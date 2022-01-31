from typing import Any, Optional
from kyc.bvn.constants import PROVIDER_MY_IDENTITY_PASS, PROVIDER_SMILE_IDENTITY
from kyc.models import ClientProviderAPIKey

import phonenumbers
from django.conf import settings

from client.models import Client
from kyc.bvn.managers.my_identity_pass import MyIdentityPassManager
from kyc.bvn.models import BVNVerification


class BVNValidationManager:
    def __init__(self, client: Client) -> None:
        """Init."""
        self.client = client
        self.errors = []
        self.provider_name = ''

    def get_object_from_provider(self, user_data: dict[str, Any]) -> Optional[BVNVerification]:
        """
        Get BVNVerification from provider response.

        return_value: tuple containing BVNVerification or None and boolean showing if provider errors were sent.
        """
        self.provider_name = user_data['provider']
        managers: dict[str, Any] = {
            PROVIDER_MY_IDENTITY_PASS: MyIdentityPassManager,
        }
        
        provider_manager = managers[self.provider_name](self.client)
        bvn_verification_object = provider_manager.get_bvn_verification_object_from_api(user_data['bvn'], user_data)

        return bvn_verification_object

    def validate_data(self, bvn_verification_object: BVNVerification, user_data: dict[str, Any]) -> bool:
        """Validate BVNVerification data gotten from provider against data supplied by client."""
        errors = []

        self.provider_name = bvn_verification_object.get_provider_display()

        if self.provider_name == PROVIDER_SMILE_IDENTITY:
            if (
                bvn_verification_object.first_name.lower() != user_data['first_name'].lower()
                or bvn_verification_object.last_name.lower() != user_data['last_name'].lower()
            ):
                errors.append('Name does not match.')
        else:
            if bvn_verification_object.first_name.lower() != user_data['first_name'].lower():
                errors.append('First name does not match.')
            if bvn_verification_object.last_name.lower() != user_data['last_name'].lower():
                errors.append('Last name does not match.')

        if (
            bvn_verification_object.date_of_birth
            and bvn_verification_object.date_of_birth.strftime('%Y-%m-%d') != user_data['date_of_birth']
        ):
            errors.append('Date of birth does not match.')

        phone_number = user_data.get('phone_number')
        if phone_number:
            try:
                formatted_phone_number = phonenumbers.format_number(
                    phonenumbers.parse(phone_number, 'NG'),
                    phonenumbers.PhoneNumberFormat.E164,
                )
            except (phonenumbers.NumberParseException, KeyError):
                formatted_phone_number = ''
            if bvn_verification_object.phone_number != formatted_phone_number:
                errors.append('Phone number does not match.')

        if errors:
            self.errors = errors
        # Return True if no errors, else return False
        return len(errors) == 0

    def validate(self, user_data: dict[str, Any]) -> dict[str, Any]:
        """Attempt to get and validate BVN Verification data from database or from providers."""

        # Check Database to confirm if BVN has been processed previously.
        try:
            bvn_verification_object = BVNVerification.objects.get(bvn=user_data['bvn'])
        except BVNVerification.DoesNotExist:
            bvn_verification_object = None

        successful = False
        if not bvn_verification_object:
            bvn_verification_object = self.get_object_from_provider(user_data)

        if bvn_verification_object:
            successful = self.validate_data(bvn_verification_object, user_data)

        return {'is_valid': successful, 'errors': self.errors}
