from django.contrib import admin
from survey.models import Scene


class SceneAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'weight')


admin.site.register(Scene, SceneAdmin)
