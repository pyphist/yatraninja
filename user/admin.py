from django.contrib import admin

from user.models import Traveller


class TravellerAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_first_name', 'get_last_name', 'mobile_number')


admin.site.register(Traveller, TravellerAdmin)