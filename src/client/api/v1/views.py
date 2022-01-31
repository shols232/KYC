from drf_yasg.utils import swagger_auto_schema

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from client.api.v1.serializers import RegisterClientSerializer
from rest_framework.permissions import AllowAny


class ClientRegistrationView(APIView):
    authentication_classes = []
    permission_classes = [
        AllowAny,
    ]
    serializer_class = RegisterClientSerializer

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: RegisterClientSerializer,
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        serializer.is_valid(raise_exception=True)
        client_api_key = serializer.save()

        return Response({'api_key': client_api_key}, status=status.HTTP_201_CREATED)
