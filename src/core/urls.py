from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from drf_yasg import openapi

SchemaView = get_schema_view(
    openapi.Info(
        title='KYC API',
        default_version='api',
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('client/', include(('client.api.v1.urls', 'client'), namespace='client_api')),
    path('kyc/', include(('kyc.api.v1.urls', 'kyc'), namespace='kyc_api')),
    # API Swagger Docs
    path('api/docs/swagger/', SchemaView.with_ui('swagger'), name='schema_swagger'),
    path('api/docs/redoc/', SchemaView.with_ui('redoc'), name='schema_redoc'),
]
