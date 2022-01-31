from django.contrib import admin

from client.models import Client, ClientApiKey

admin.site.register(Client, admin.ModelAdmin)
admin.site.register(ClientApiKey, admin.ModelAdmin)
