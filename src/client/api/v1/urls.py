from django.urls import path
from client.api.v1.views import ClientRegistrationView

urlpatterns = [path('', ClientRegistrationView.as_view(), name='client_register')]
