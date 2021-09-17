from .models import (
    EventSignup,
    ParkingFacility,
    ParkingFacilityCondition,
    ParkingFacilityOccupancy,
    Signup,
    Station,
    SurveyStation,
)
from django.contrib import admin
from fixmyapp.admin import FMBGeoAdmin
from reversion.admin import VersionAdmin


class SignupAdmin(admin.ModelAdmin):
    list_display = ('email',)


class EventSignupAdmin(admin.ModelAdmin):
    list_display = ('event_title', 'email')


class StationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'community')
    fields = (
        'id',
        'name',
        'community',
        'post_code',
        'travellers',
        'is_long_distance',
        'is_light_rail',
        'is_subway',
        'location',
    )


class SurveyStationAdmin(admin.ModelAdmin):
    list_display = ('created_date', 'session', 'station')


class ParkingFacilityConditionInline(admin.StackedInline):
    extra = 1
    list_display = 'value'
    model = ParkingFacilityCondition


class ParkingFacilityOccupancyInline(admin.StackedInline):
    extra = 1
    list_display = 'value'
    model = ParkingFacilityOccupancy


class ParkingFacilityAdmin(FMBGeoAdmin, VersionAdmin):
    list_display = (
        'station',
        'capacity',
        'type',
        'parking_garage',
        'covered',
        'two_tier',
        'secured',
        'confirmations',
    )
    inlines = (ParkingFacilityConditionInline, ParkingFacilityOccupancyInline)


admin.site.register(Signup, SignupAdmin)
admin.site.register(EventSignup, EventSignupAdmin)
admin.site.register(Station, StationAdmin)
admin.site.register(SurveyStation, SurveyStationAdmin)
admin.site.register(ParkingFacility, ParkingFacilityAdmin)
