from django.core.files.uploadedfile import SimpleUploadedFile

from client.models import Client, ClientApiKey


class TestUtils:
    @staticmethod
    def generate_client_auth_headers(client: Client) -> dict[str, str]:
        """Generate the authentication headers for a logged in client."""
        key, _ = ClientApiKey.objects.get_or_create(
            client=client, is_active=True, defaults={'api_key': 'some_api_key'}
        )
        return {'HTTP_AUTHORIZATION': f'Token {key.api_key}'}