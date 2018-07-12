from django.urls import path
from .views import (
    PlanningSectionDetail,
    planning_sections,
    planning_sections_in_progress,
    profile
)


urlpatterns = [
    path(
        'planning-sections',
        planning_sections,
        name='planning-sections'
    ),
    path(
        'planning-sections/<int:pk>',
        PlanningSectionDetail.as_view(),
        name='planning-section-detail'
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
