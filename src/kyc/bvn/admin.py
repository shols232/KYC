from django.contrib import admin

from kyc.bvn.models import BVNVerification


class BVNVerificationAdmin(admin.ModelAdmin):
    search_fields = ('id', 'bvn', 'phone_number')
    list_filter = (
        'client',
        'provider',
    )


admin.site.register(BVNVerification, BVNVerificationAdmin)
