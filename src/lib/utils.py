import logging
from typing import Any

from dateutil.parser import parserinfo
from django.conf import settings
from requests import Response

from client.models import Client
# from kyc.banking.constants import BANK_CODES
from utilities.models import APIResponse

LOGGER = logging.getLogger(__name__)


def log_api_response(response: Response) -> APIResponse:
    """Log response from an API request."""

    if not response.request.method or not response.request.url:
        raise AssertionError('Invalid request data')

    request_body = response.request.body or ''
    if isinstance(request_body, bytes):
        request_body = request_body.decode(settings.DEFAULT_ENCODING)

    return APIResponse.objects.create(
        method=response.request.method,
        url=response.request.url,
        data=request_body,
        response=response.content.decode(settings.DEFAULT_ENCODING),
        status_code=response.status_code,
    )


def get_bank_code(bank: str, provider: str) -> str:
    """Return the bank code based on the provider."""
    bank_code = ''
    try:
        # bank_code = BANK_CODES[provider.lower()][bank.lower()]
        pass
    except KeyError:
        LOGGER.exception(
            'kyc::banking::utils::get_bank_code: Bank or provider not available',
            extra={'bank': bank, 'provider': provider},
        )

        raise
    return bank_code


def clean_name(api_name: str) -> list[str]:
    """Clean names returned from validation APIs to match with names in DB."""

    # strip outer non-letter characters, remove periods in the middle and split the string
    names_list = api_name.strip(' -.,').replace('.', ' ').replace(',', ' ').lower().split()

    return names_list


class ParseYearLastCentury(parserinfo):
    """
    Older 2 digit years from last century are put in the future by dateutil.parser. Example, '46' is parsed as '2046'.

    As a result, convertyear needs to be redefined.

    See https://dateutil.readthedocs.io/en/stable/parser.html for more details.

    Only use this class when date returned by parser is in the future.
    """

    def convertyear(self, year: int, century_specified: bool = False) -> int:
        """Convert 2 digit year to 4 digit year from last century."""
        if year < 100:
            year += 1900
        return year


def match_name(input_set: Any, matching_set: Any) -> bool:
    """Match two sets."""
    # Both sets have same content and not necessarily same order:
    if input_set == matching_set:
        return True

    # If not equal rest of matching only when more than one word to avoid positive negatives
    if len(input_set) > 1 and len(matching_set) > 1:

        # Check if input set is subset of matching set or viceversa
        if input_set.issubset(matching_set) or matching_set.issubset(input_set):
            return True

        # Check similar, when for example a typo or something
        # Need be careful to not abuse in matching -> accept 1 wrong word
        threshold_wrong_words = 1
        intersection_set = input_set.intersection(matching_set)
        if len(intersection_set) + threshold_wrong_words == len(input_set) or len(
            intersection_set
        ) + threshold_wrong_words == len(matching_set):
            return True
    return False


def get_kyc_providers_order(kyc_providers_settings: dict[str, Any]) -> list[dict[str, Any]]:
    """Return sorted KYC providers order."""
    order = [
        {'name': provider_name, 'priority': provider_settings['priority']}
        for provider_name, provider_settings in kyc_providers_settings.items()
        if provider_settings.get('priority') is not None
    ]
    order.sort(key=lambda item: item['priority'])
    return order
