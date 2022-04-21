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
from django.conf.urls.static import static


def reset(request, uid, token):
    url = settings.DJOSER.get('PASSWORD_RESET_CONFIRM_FRONTEND_URL')
    return redirect(url.format(uid=uid, token=token))


def activate(request, uid, token):
    url = settings.DJOSER.get('ACTIVATION_FRONTEND_URL')
    query = request.GET.urlencode()
    return redirect(url.format(uid=uid, token=token, query=query))


urlpatterns = [
    path(
        'openapi',
        get_schema_view(
            title="Your Project", description="API for all things …", version="1.0.0"
        ),
        name='openapi-schema',
    ),
    path(
        'swagger-ui/',
        TemplateView.as_view(
            template_name='swagger-ui.html',
            extra_context={'schema_url': 'openapi-schema'},
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
