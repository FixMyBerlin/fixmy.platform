import dateutil.parser
import boto3
from datetime import datetime, timezone
from django.conf import settings
from django.core import mail
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response

from .models import EventPermit
from .serializers import EventPermitSerializer, EventPermitDocumentSerializer


class EventPermitView(APIView):
    permission_classes = (permissions.AllowAny,)

    def _send_registration_confirmation(self, recipient, request):
        """Send a registration confirmation email notice"""
        subject = 'Ihr Antrag bei Xhain-Terrassen'
        body = render_to_string('xhain/notice_event_registered.txt', request=request)
        mail.send_mail(
            subject, body, settings.DEFAULT_FROM_EMAIL, [recipient], fail_silently=True
        )

    def get(self, request, campaign, pk, access_key=None):
        """Request existing permit data"""
        result = get_object_or_404(EventPermit, pk=pk)

        serialization = EventPermitSerializer(result).data
        return Response(serialization)

    def post(self, request, campaign):
        """Adds new event permit application."""

        def event_permit_signups_open():
            try:
                start = dateutil.parser.parse(settings.EVENT_SIGNUPS_OPEN)
                end = dateutil.parser.parse(settings.EVENT_SIGNUPS_CLOSE)
            except TypeError:
                # No explicit start and end times defined
                return True
            rv = start < datetime.now(tz=timezone.utc) < end
            return rv

        if not settings.TOGGLE_EVENT_SIGNUPS or not event_permit_signups_open():
            return Response(
                'Signups are currently not open',
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )

        serializer = EventPermitSerializer(data=request.data)

        if serializer.is_valid():
            instance = serializer.save(
                campaign=campaign,
                status=EventPermit.STATUS_REGISTERED,
                insurance=request.data.get('insuranceS3'),
                agreement=request.data.get('agreementS3'),
                setup_sketch=request.data.get('setup_sketchS3'),
                public_benefit=request.data.get('public_benefitS3'),
                application_received=datetime.now(tz=timezone.utc),
            )
            self._send_registration_confirmation(instance.email, request)
            return Response(request.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EventPermitDocumentView(APIView):
    permission_classes = (permissions.AllowAny,)
    parser_classes = [FileUploadParser]
    serializer_class = EventPermitDocumentSerializer

    def post(self, request, campaign, doc_name, fname):
        """Upload a document for an application"""
        if not settings.TOGGLE_EVENT_SIGNUPS:
            return Response(
                'Registration is currently not open',
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )

        if doc_name not in ['insurance', 'agreement', 'public_benefit', 'setup_sketch']:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        s3_client = boto3.client('s3')
        sort_path = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        s3_key = f"{campaign}/events/{doc_name}/{sort_path}/{fname}"

        try:
            s3_client.upload_fileobj(
                request.data['file'], settings.AWS_STORAGE_BUCKET_NAME, s3_key
            )
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response({'path': s3_key})
