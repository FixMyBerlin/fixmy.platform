from django.urls import path
from django.views.decorators.cache import cache_page
from .models import Project, Report
from .views import (
    feedback,
    GastroSignupView,
    LikedByUserProjectList,
    LikedByUserReportList,
    LikeView,
    newsletter_signup,
    PlayStreetView,
    profile,
    ProjectDetail,
    ProjectList,
    ReportDetail,
    ReportList,
    SectionDetail,
    SectionList,
)


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
        'reports',
        ReportList.as_view(),
        name='report-list'
    ),
    path(
        'reports/<int:pk>',
        ReportDetail.as_view(),
        name='report-detail'
    ),
    path(
        'reports/<int:pk>/likes',
        LikeView.as_view(),
        {'model': Report},
        name='likes-reports',
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
    path(
        'users/me/liked/reports',
        LikedByUserReportList.as_view(),
        name='reports-liked-by-user'
    )
]
