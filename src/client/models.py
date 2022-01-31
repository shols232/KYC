from django.db import models

from utilities.models import BaseAbstractModel


class Client(BaseAbstractModel):
    """Model that represents a client entity."""

    # # Webhook Status
    # DIGEST_TYPES_SHA512 = 0
    # DIGEST_TYPES = ((DIGEST_TYPES_SHA512, 'sha512'),)  # hashlib.sha512

    name = models.CharField(max_length=50)
    email = models.EmailField()
    domain = models.CharField(max_length=200)

    # digest_type = models.IntegerField(choices=DIGEST_TYPES, default=DIGEST_TYPES_SHA512)
    # digest_secret = models.CharField(max_length=200)
    # webhook_url = models.URLField()

    class Meta:
        """Class meta."""

        unique_together = [
            ['name', 'email'],
        ]

    def __str__(self) -> str:
        """
        Unicode representation for a Client model.

        :return: string
        """
        return f'Client: {self.name}'

    @property
    def is_authenticated(self) -> bool:
        """
        Override the is_authenticated method.

        The Client is not an actual Django user, so it doesn't have sessions or login.
        """
        return True


class ClientApiKey(BaseAbstractModel):
    """Model that represents a clients API KEY."""

    client = models.ForeignKey(to='client.Client', on_delete=models.PROTECT, related_name='clientapikey_set')
    is_active = models.BooleanField(default=True)
    api_key = models.CharField(max_length=200, unique=True)

    def __str__(self) -> str:
        """
        Unicode representation for a ClientApiKey model.

        :return: string
        """
        return f'ClientApiKey: {self.client.name}'
