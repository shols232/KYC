from drf_yasg.utils import swagger_auto_schema

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from kyc.api.v1.serializers import ClientProviderAPIKeySerializer
from client.authentication import ClientAuthentication


class ClientProviderAPIKeyCreateView(APIView):
    authentication_classes = [ClientAuthentication]
    serializer_class = ClientProviderAPIKeySerializer

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: ClientProviderAPIKeySerializer,
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        serializer.is_valid(raise_exception=True)

        return Response({'action': 'success'}, status=status.HTTP_200_OK)
