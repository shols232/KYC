from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from kyc.bvn.constants import PROVIDERS
from utilities.models import BaseAbstractModel


class BVNVerification(BaseAbstractModel):
    """Model that represents a BVNVerification."""

    client = models.ForeignKey(to='client.Client', on_delete=models.PROTECT)
    provider = models.CharField(max_length=25, choices=PROVIDERS, blank=True)

    bvn = models.CharField(max_length=15, unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    phone_number = PhoneNumberField(blank=True)
    date_of_birth = models.DateField(null=True)
    api_responses = models.ManyToManyField(
        to='utilities.APIResponse', blank=True, related_name='bvnverification_api_responses_set'
    )

    def __str__(self) -> str:
        """
        Unicode representation for an BVNVerification model.

        :return: string
        """
        return f'BVNVerification: {self.id}: {self.bvn} - {self.client.name} - {self.datetime_created}'
