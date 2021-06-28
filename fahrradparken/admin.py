from django.contrib import admin

from .models import Signup, EventSignup


class SignupAdmin(admin.ModelAdmin):
    list_display = ('email',)


class EventSignupAdmin(admin.ModelAdmin):
    list_display = ('event_title', 'email')


admin.site.register(Signup, SignupAdmin)
admin.site.register(EventSignup, EventSignupAdmin)
