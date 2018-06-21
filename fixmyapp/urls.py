from django.urls import path
from .views import planning_sections, planning_sections_in_progress, profile


urlpatterns = [
    path(
        'planning-sections',
        planning_sections,
        name='planning-sections'
    ),
    path(
        'planning-sections/in-progress',
        planning_sections_in_progress,
        name='planning-sections-in-progress'
    ),
    path(
        'profiles/<str:profile_id>',
        profile,
        name='profile'
    )
]
