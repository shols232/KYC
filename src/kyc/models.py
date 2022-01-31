from django.db import models

from utilities.models import BaseAbstractModel

class ClientProviderAPIKey(BaseAbstractModel):

    PROVIDER_MY_IDENTITY_PASS = "MIP"
    PROVIDER_SMILE_IDENTITY = "SI"
    PROVIDERS = (
        (PROVIDER_MY_IDENTITY_PASS, 'My Identity Pass'),
        (PROVIDER_SMILE_IDENTITY, 'Smile Identity'),
    )

    client = models.ForeignKey(to='client.Client', on_delete=models.PROTECT)
    provider = models.CharField(max_length=25, choices=PROVIDERS)
    api_key = models.CharField(max_length=500)

    def __str__(self) -> str:
        return f'{self.client.name} {self.provider}'
