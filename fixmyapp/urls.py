from django.urls import path
from .views import planning_sections, edges


urlpatterns = [
    path(
        'planning-sections',
        planning_sections,
        name='planning-sections'
    ),
    path('edges', edges, name='edges')
]
