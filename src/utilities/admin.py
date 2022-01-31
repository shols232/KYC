from django.contrib import admin

from .models import APIResponse

class APIResponseAdmin(admin.ModelAdmin):
    search_fields = ('id',)


admin.site.register(APIResponse, APIResponseAdmin)
