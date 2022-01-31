import uuid

from django.db import models


class BaseAbstractModel(models.Model):
    """Base model for all models."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    datetime_updated = models.DateTimeField(auto_now=True)
    datetime_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Class meta."""

        abstract = True


class APIResponse(BaseAbstractModel):
    """Model that represents all API responses received."""

    url = models.CharField(max_length=255, editable=False)
    method = models.CharField(max_length=7, editable=False)
    data = models.TextField(blank=True, editable=False)
    response = models.TextField(editable=False)
    status_code = models.IntegerField(editable=False)

    def __str__(self) -> str:
        """
        Unicode representation for an APIResponse model.

        :return: string
        """
        return f'APIResponse: {self.method} {self.url}: {self.status_code} - {self.datetime_created}'
