"""fixmydjango URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib.gis import admin
from django.shortcuts import redirect
from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.schemas import get_schema_view
from rest_framework.schemas.openapi import SchemaGenerator


def reset(request, uid, token):
    url = settings.DJOSER.get('PASSWORD_RESET_CONFIRM_FRONTEND_URL')
    return redirect(url.format(uid=uid, token=token))


def activate(request, uid, token):
    url = settings.DJOSER.get('ACTIVATION_FRONTEND_URL')
    query = request.GET.urlencode()
    return redirect(url.format(uid=uid, token=token, query=query))


# specify wich routes should be exposed in the /openapi endpoint
schema_url_patterns = [
    path('api/fahrradparken/', include('fahrradparken.urls')),
]

# modify the generated schema s.t. there are only get methods
class GetSchemaGenerator(SchemaGenerator):
    def get_schema(self, *args, **kwargs):
        schema = super().get_schema(*args, **kwargs)
        paths = schema['paths']
        ro_paths = {}
        for p in paths:
            if 'get' in paths[p]:
                ro_paths[p] = {'get': paths[p]['get']}
        print(ro_paths)
        schema['paths'] = ro_paths
        return schema


urlpatterns = [
    path(
        'api/fahrradparken/openapi',
        get_schema_view(
            title="The Fahrradparken-API documentation",
            description="The API documentation for radparken.info",
            version="1.0.0",
            patterns=schema_url_patterns,
            generator_class=GetSchemaGenerator,
        ),
        name='radparken-openapi',
    ),
    path(
        'api/fahrradparken/swagger-ui/',
        TemplateView.as_view(
            template_name='swagger-ui.html',
            extra_context={'schema_url': 'radparken-openapi'},
        ),
        name='swagger-ui',
    ),
    path('admin/', admin.site.urls),
    path('api/', include('fixmyapp.urls')),
    path('api/', include('reports.urls')),
    path('api/', include('permits.urls')),
    path('api/fahrradparken/', include('fahrradparken.urls')),
    path('api/', include('djoser.urls')),
    path('api/', include('djoser.urls.jwt')),
    path('api/survey/', include('survey.urls')),
    path('markdownx/', include('markdownx.urls')),
    path('reset/<str:uid>/<str:token>', reset, name='reset'),
    path('activate/<str:uid>/<str:token>', activate, name='activate'),
]
