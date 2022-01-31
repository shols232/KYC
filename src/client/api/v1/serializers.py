from typing import Any
from rest_framework.serializers import ModelSerializer, ValidationError
from client.models import Client, ClientApiKey


class ClientSerializer(ModelSerializer[Client]):
    class Meta:
        fields = ['name', 'email', 'domain']


class RegisterClientSerializer(ModelSerializer):
    """Serializer for user registeration"""

    class Meta:
        model = Client
        fields = ['id', 'name', 'email', 'domain']
        read_only_fields = ['id']

    def validate(self, attrs) -> dict[str, Any]:
        if Client.objects.filter(email=attrs["email"]).exists():
            # if email exist raise error
            raise ValidationError("A client with this email already exists")

        return attrs

    def create(self, validated_data) -> str:
        client = Client.objects.create(**validated_data)
        client_api_key: ClientApiKey = ClientApiKey.objects.create(client=client)
        return client_api_key.api_key
