from .models import (
    EventSignup,
    ParkingFacility,
    ParkingFacilityCondition,
    ParkingFacilityOccupancy,
    ParkingFacilityPhoto,
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
    search_fields = ('id',)


class SurveyStationAdmin(admin.ModelAdmin):
    list_display = ('created_date', 'session', 'station', 'is_photo_published')
    list_filter = (("photo", admin.EmptyFieldListFilter),)


class ParkingFacilityConditionInline(admin.StackedInline):
    extra = 1
    list_display = 'value'
    model = ParkingFacilityCondition


class ParkingFacilityOccupancyInline(admin.StackedInline):
    extra = 1
    list_display = 'value'
    model = ParkingFacilityOccupancy


class ParkingFacilityPhotoInline(admin.TabularInline):
    fields = ('photo_url', 'description', 'terms_accepted', 'is_published')
    model = ParkingFacilityPhoto


class ParkingFacilityAdmin(FMBGeoAdmin, VersionAdmin):
    autocomplete_fields = ('station',)
    inlines = (
        ParkingFacilityConditionInline,
        ParkingFacilityOccupancyInline,
        ParkingFacilityPhotoInline,
    )
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


admin.site.register(Signup, SignupAdmin)
admin.site.register(EventSignup, EventSignupAdmin)
admin.site.register(Station, StationAdmin)
admin.site.register(SurveyStation, SurveyStationAdmin)
admin.site.register(ParkingFacility, ParkingFacilityAdmin)
