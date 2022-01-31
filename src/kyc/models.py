from django.db import models

from utilities.models import BaseAbstractModel

class ClientProviderAPIKey(BaseAbstractModel):

    PROVIDER_MY_IDENTITY_PASS = "MIP"
    PROVIDERS = (
        (PROVIDER_MY_IDENTITY_PASS, 'My Identity Pass'),
    )

    client = models.ForeignKey(to='client.Client', on_delete=models.PROTECT)
    provider = models.CharField(max_length=25, choices=PROVIDERS)
    api_key = models.CharField(max_length=150)

    def __str__(self) -> str:
        return f'{self.client.name} {self.provider}'
