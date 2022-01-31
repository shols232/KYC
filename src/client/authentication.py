from __future__ import annotations

import logging

from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication

from .models import ClientApiKey, Client

LOGGER = logging.getLogger(__name__)


class ClientAuthentication(TokenAuthentication):
    """Authenticate a client using its API token."""

    def authenticate_credentials(self, key: str) -> tuple[Client, ClientApiKey]:
        """Override token retrieval by the Client's token."""
        try:
            api_key: ClientApiKey = ClientApiKey.objects.get(api_key=key, is_active=True)
        except ClientApiKey.DoesNotExist as exception:
            raise exceptions.AuthenticationFailed(_('Invalid token.')) from exception
        except ClientApiKey.MultipleObjectsReturned as exception:
            LOGGER.exception(
                'client::authentication::ClientAuthentication::authenticate:: More than one API returned.',
            )
            raise exceptions.AuthenticationFailed(_('Invalid token.')) from exception

        return api_key.client, api_key
