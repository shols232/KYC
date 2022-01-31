from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('client/', include(('client.api.v1.urls', 'client'), namespace='client_api')),
    path('kyc/', include(('kyc.api.v1.urls', 'kyc'), namespace='kyc_api')),
]
