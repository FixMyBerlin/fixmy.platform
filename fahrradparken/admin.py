from django.contrib import admin

from .models import Signup, EventSignup, Station


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


admin.site.register(Signup, SignupAdmin)
admin.site.register(EventSignup, EventSignupAdmin)
admin.site.register(Station, StationAdmin)
