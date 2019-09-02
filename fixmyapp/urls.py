from django.urls import path
from django.views.decorators.cache import cache_page
from .models import Planning, Project, Report
from .views import (
    LikeView,
    PlanningDetail,
    PlanningList,
    PlanningSectionDetail,
    PlanningSectionList,
    ProjectDetail,
    ProjectList,
    ReportDetail,
    ReportList,
    SectionList,
    SectionDetail,
    feedback,
    newsletter_signup,
    profile
)


urlpatterns = [
    path(
        'feedback',
        feedback,
        name='feedback'
    ),
    path(
        'newsletter-signup',
        newsletter_signup,
        name='newsletter-signup'
    ),
    path(
        'plannings',
        cache_page(60 * 60 * 4)(PlanningList.as_view()),
        name='planning-list'
    ),
    path(
        'plannings/<int:pk>',
        PlanningDetail.as_view(),
        name='planning-detail'
    ),
    path(
        'plannings/<int:pk>/likes',
        LikeView.as_view(),
        {'model': Planning},
        name='likes-plannings'
    ),
    path(
        'planning-sections',
        PlanningSectionList.as_view(),
        name='planningsection-list'
    ),
    path(
        'planning-sections/<int:pk>',
        PlanningSectionDetail.as_view(),
        name='planningsection-detail'
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
    )
]
