from django.conf.urls import url
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import planning_sections, planning_sections_in_progress


router = DefaultRouter()

urlpatterns = [
    url(r'^', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
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
]
