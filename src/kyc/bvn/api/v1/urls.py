from django.urls import path

from kyc.bvn.api.v1.views import ValidateBVNView

urlpatterns = [
    path('validate/', ValidateBVNView.as_view(), name='validate_bvn'),
]
