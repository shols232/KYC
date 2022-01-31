from django.contrib import admin

from kyc.models import ClientProviderAPIKey


class ClientProviderAPIKeyAdmin(admin.ModelAdmin):
    search_fields = ('id', 'provider',)
    list_filter = (
        'client',
        'provider',
    )


admin.site.register(ClientProviderAPIKey, ClientProviderAPIKeyAdmin)
