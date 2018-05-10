from django.urls import path
from .views import planning_sections


urlpatterns = [
    path(
        'planning-sections',
        planning_sections,
        name='planning-sections'
    )
]
