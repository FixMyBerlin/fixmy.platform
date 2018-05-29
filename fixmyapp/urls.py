from django.conf.urls import url
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from accounts.views import UserCreate
from . import views
router = DefaultRouter()

urlpatterns = [
    url(r'^', include(router.urls)),
    path(
        'planning-sections',
        views.planning_sections,
        name='planning-sections'
    ),
    path(
        'planning-sections/in-progress',
        views.planning_sections_in_progress,
        name='planning-sections-in-progress'
    ),
    path('planning-sections/upload',
         views.UploadPlanningSections.as_view(),
         name='planning-sections-upload',
    ),
    path('edges/upload',
         views.UploadEdges.as_view(),
         name='edges-upload',
    ),
    url(r'^users$', UserCreate.as_view(), name='account-create'),
    path('api-auth/', include('rest_framework.urls')),
]
