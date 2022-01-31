from typing import Any
import uuid
from rest_framework.serializers import ModelSerializer, ValidationError
from client.models import Client, ClientApiKey
from kyc.models import ClientProviderAPIKey


class ClientProviderAPIKeySerializer(ModelSerializer):
    """Serializer for Client API Key serialization."""

    class Meta:
        model = ClientProviderAPIKey
        fields = ['id', 'provider', 'is_active', 'api_key']
        read_only_fields = ['id']

    def create(self, validated_data) -> ClientProviderAPIKey:
        client = self.context['client']
        # If this provider already exists for this client, UPDATE IT.
        client_provider, created = ClientProviderAPIKey.objects.get_or_create(client=client, provider=validated_data["provider"])
        
        # It already exists.
        if not created:
            client_provider.api_key = str(uuid.uuid4())
            client_provider.save(update_fields=['api_key'])

        return client_provider
