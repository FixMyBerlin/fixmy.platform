import uuid
from django_auto_prefetching import AutoPrefetchViewSetMixin
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password, make_password
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination

from fixmyapp.models import NoticeSetting
from .models import Like, Report, BikeStands
from .serializers import ReportSerializer


class DefaultPagination(PageNumberPagination):
    max_page_size = 1000
    page_size = 10
    page_size_query_param = 'page_size'


class LikedByUserReportList(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = DefaultPagination
    serializer_class = ReportSerializer

    def get_queryset(self):
        return Report.objects.filter(
            likes__in=Like.objects.filter(user=self.request.user)
        ).order_by('id')


class ReportList(AutoPrefetchViewSetMixin, generics.ListCreateAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = (
        Report.objects.filter(published=1)
        .select_related('bikestands')
        .prefetch_related('origin', 'likes')
    )
    serializer_class = ReportSerializer

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save()


class ReportDetail(generics.RetrieveUpdateAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = Report.objects.filter(published=1)
    serializer_class = ReportSerializer

    def perform_update(self, serializer):
        """Allows associating a user with a report instance once.

        Once a user is associated with a report, no further updates are allowed
        via the API.
        """
        if self.get_object().user:
            raise PermissionDenied
        else:
            super(ReportDetail, self).perform_update(serializer)


class UnsubscribeView(TemplateView):
    template_name = f"unsubscribe_{NoticeSetting.REPORT_UPDATE_KIND}.html"

    def get(self, request, user_id, access_key, *args, **kwargs):
        notice_setting = get_object_or_404(
            NoticeSetting, user_id=user_id, kind=NoticeSetting.REPORT_UPDATE_KIND
        )

        try:
            if notice_setting.access_key != uuid.UUID(access_key):
                return HttpResponseForbidden()
        except ValueError:
            return HttpResponseForbidden()

        notice_setting.send = False
        notice_setting.save()

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['FRONTEND_URL'] = settings.FRONTEND_URL
        return context


@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def report_stats(request):
    reports = BikeStands.objects.all()

    REPORT_STATUSES = [
        Report.STATUS_REPORT_NEW,
        Report.STATUS_REPORT_VERIFICATION,
        Report.STATUS_REPORT_ACCEPTED,
        Report.STATUS_REPORT_REJECTED,
        Report.STATUS_REPORT_INACTIVE,
    ]

    PLANNINGS_STATUSES = [
        Report.STATUS_PLANNING,
        Report.STATUS_TENDER,
        Report.STATUS_EXECUTION,
        Report.STATUS_DONE,
    ]

    report_bike_stands = [r.number for r in reports if r.status in REPORT_STATUSES]
    planning_bike_stands = [r.number for r in reports if r.status in PLANNINGS_STATUSES]

    rv = {
        'reports': len(report_bike_stands),
        'reportsStands': sum(report_bike_stands),
        'plannings': len(planning_bike_stands),
        'planningsStands': sum(planning_bike_stands),
    }
    return Response(rv)