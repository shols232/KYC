from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from client.authentication import ClientAuthentication
from client.models import Client
from kyc.bvn.api.v1.serializers import (
    BVNValidationResponseSerializer,
    ValidateBVNSerializer,
)
from kyc.bvn.utils import BVNValidationManager


class ValidateBVNView(APIView):

    serializer_class = ValidateBVNSerializer
    authentication_classes = (ClientAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        request_body=ValidateBVNSerializer,
        responses={
            status.HTTP_200_OK: BVNValidationResponseSerializer,
        },
    )
    def post(self, request: Request) -> Response:
        """Validate a BVN."""

        client: Client = request.user

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        manager = BVNValidationManager(client=client)
        response = manager.validate(serializer.data)

        if 'is_valid' in response:
            response_data = BVNValidationResponseSerializer().to_representation(response)
            response_status: int = status.HTTP_200_OK
        else:
            response_data = {'success': False}
            response_status = status.HTTP_400_BAD_REQUEST

        return Response(data=response_data, status=response_status)
