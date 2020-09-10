from django.core.exceptions import PermissionDenied
from rest_framework import generics, permissions
from rest_framework.pagination import PageNumberPagination

from .models import Like, Report
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


class ReportList(generics.ListCreateAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = Report.objects.filter(published=1).prefetch_related(
        'likes', 'bikestands'
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
