from django.urls import path
from django.views.decorators.cache import cache_page
from .models import Project
from .views import (
    feedback,
    GastroCertificateView,
    GastroRenewalView,
    GastroSignupView,
    LikedByUserProjectList,
    LikeView,
    newsletter_signup,
    PlayStreetView,
    profile,
    ProjectDetail,
    ProjectList,
    SectionDetail,
    SectionList,
)

# fmt: off
urlpatterns = [
    path(
        'feedback',
        feedback,
        name='feedback'
    ),
    path(
        'gastro/<str:campaign>',
        GastroSignupView.as_view(),
        name='gastro-signups'
    ),
    path(
        'gastro/<str:campaign>/certificate/direct/<str:fname>',
        GastroCertificateView.as_view(),
        name='gastro-certificate'
    ),
    path(
        'gastro/<str:campaign>/certificate/<int:pk>/<str:access_key>',
        GastroCertificateView.as_view(),
        name='gastro-certificate-existing-signup'
    ),
    path(
        'gastro/<str:campaign>/renewal/<int:pk>/<str:access_key>',
        GastroRenewalView.as_view(),
        name='gastro-signups-detail-restricted'
    ),
    path(
        'gastro/<str:campaign>/<int:pk>',
        GastroSignupView.as_view(),
        name='gastro-signups-detail'
    ),
    path(
        'gastro/<str:campaign>/<int:pk>/<str:access_key>',
        GastroSignupView.as_view(),
        name='gastro-signups-detail-restricted'
    ),
    path(
        'newsletter-signup',
        newsletter_signup,
        name='newsletter-signup'
    ),
    path(
        'profiles/<str:profile_id>',
        profile,
        name='profile-detail'
    ),
    path(
        'projects',
        cache_page(60 * 60 * 4)(ProjectList.as_view()),
        name='project-list'
    ),
    path(
        'projects/<int:pk>',
        ProjectDetail.as_view(),
        name='project-detail'
    ),
    path(
        'projects/<int:pk>/likes',
        LikeView.as_view(),
        {'model': Project},
        name='likes-projects'
    ),
    path(
        'sections',
        SectionList.as_view(),
        name='section-list'
    ),
    path(
        'sections/<int:pk>',
        SectionDetail.as_view(),
        name='section-detail'
    ),
    path(
        'playstreets/<str:campaign>',
        PlayStreetView.as_view(),
        name='playstreets'
    ),
    path(
        'users/me/liked/projects',
        LikedByUserProjectList.as_view(),
        name='projects-liked-by-user'
    ),
]
# fmt: on
