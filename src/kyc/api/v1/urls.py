from django.urls import include, path
from .views import ClientProviderAPIKeyCreateView

urlpatterns = [
    path('v1/bvn/', include(('kyc.bvn.api.v1.urls', 'bvn_v1'), namespace='bvn_api_v1')),
    path('v1/provider-key/create/', ClientProviderAPIKeyCreateView.as_view(), name='provider_key_create')
]
