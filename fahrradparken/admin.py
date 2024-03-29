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
from django.utils.translation import gettext_lazy as _
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
    list_filter = (('photo', admin.EmptyFieldListFilter),)


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
    readonly_fields = ('terms_accepted',)


class ParkingFacilityAdmin(FMBGeoAdmin, VersionAdmin):
    autocomplete_fields = ('station',)
    inlines = (
        ParkingFacilityConditionInline,
        ParkingFacilityOccupancyInline,
        ParkingFacilityPhotoInline,
    )
    list_display = (
        'external_id',
        'station',
        'capacity',
        'truncated_fingerprint',
        'modified_date',
    )
    list_filter = (
        'confirmations',
        'type',
        'parking_garage',
        'covered',
        'two_tier',
        'secured',
        'photos__is_published',
    )
    readonly_fields = ('fingerprint',)
    search_fields = ('external_id', 'station__name')

    def truncated_fingerprint(self, obj):
        return obj.fingerprint[:10] if obj.fingerprint else ''

    truncated_fingerprint.short_description = _('fingerprint')
    truncated_fingerprint.admin_order_field = 'fingerprint'


# TODO Delete, will not be used.
admin.site.register(Signup, SignupAdmin)
# TODO Delete, will not be used.
admin.site.register(EventSignup, EventSignupAdmin)
admin.site.register(Station, StationAdmin)
admin.site.register(SurveyStation, SurveyStationAdmin)
admin.site.register(ParkingFacility, ParkingFacilityAdmin)
