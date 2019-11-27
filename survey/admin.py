from django.contrib import admin
from survey.models import Scene, Session


class SceneAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'weight')


class SessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_date')


admin.site.register(Scene, SceneAdmin)
admin.site.register(Session, SessionAdmin)
