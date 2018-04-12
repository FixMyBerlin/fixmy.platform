from django.urls import path
from .views import projects, edges


urlpatterns = [
    path('projects', projects, name='projects'),
    path('edges', edges, name='edges')
]
