from django.contrib import admin

from companion.models import Request, Companion


class RequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'request_owner', 'trip_type', 'traveler_type', 'sponsorship')


class CompanionAdmin(admin.ModelAdmin):
    list_display = ('id', 'request', 'requestor', 'message')


admin.site.register(Request, RequestAdmin)
admin.site.register(Companion, CompanionAdmin)