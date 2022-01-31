import re
from typing import Any

from rest_framework.fields import (
    BooleanField,
    CharField,
    DateField,
    DictField,
    ListField,
)
from rest_framework.serializers import Serializer, ValidationError

from kyc.bvn.constants import VALID_BVN_PROVIDERS_LIST


class ValidateBVNSerializer(Serializer[dict[str, Any]]):
    first_name = CharField()
    last_name = CharField()
    bvn = CharField(min_length=11, max_length=11)
    phone_number = CharField(required=False)
    date_of_birth = DateField()
    providers = ListField(child=CharField(), required=False, allow_empty=False)

    def validate_bvn(self, value: str) -> str:
        """Validate BVN."""
        reg = re.compile(r'^\d{11}$')
        if not reg.match(value):
            raise ValidationError('BVN must be digits.')
        return value

    def validate_provider(self, value: str) -> list[str]:
        """Validate provider."""
        if value not in VALID_BVN_PROVIDERS_LIST:
            raise ValidationError(f'{value} is an invalid provider value.')

        return value


class BVNValidationResponseSerializer(Serializer[dict[str, Any]]):
    is_valid = BooleanField(read_only=True)
    errors = ListField()
