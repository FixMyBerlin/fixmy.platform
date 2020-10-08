from collections import defaultdict
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import get_connection, EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template.loader import get_template
from django.contrib.gis.geos import Point

from fixmyapp.models import NoticeSetting
from reports.models import StatusNotice, Report, BikeStands

# Statuses for which notifications will be sent
NOTIFICATION_STATUSES = [
    Report.STATUS_PLANNING,
    Report.STATUS_REPORT_REJECTED,
    Report.STATUS_REPORT_ACCEPTED,
    Report.STATUS_EXECUTION,
    Report.STATUS_DONE,
]


class Command(BaseCommand):
    help = 'Send queued notifications for report status updates'
    template_txt = get_template("email/report_update.txt")
    template_html = get_template("email/report_update.html")
    email_data = []

    def add_arguments(self, parser):
        parser.add_argument(
            '--send_samples',
            type=str,
            default=None,
            help='send sample emails to preview contents',
        )

    def handle(self, *args, **options):
        self.email_data = []

        if options['send_samples'] is not None:
            self.sample_email(options['send_samples'])
            return

        notices = (
            StatusNotice.objects.filter(sent=False)
            .select_related()
            .order_by('user_id')
            .all()
        )

        if len(notices) == 0:
            self.stdout.write("All notifications were sent already")
            return

        self.stdout.write(f"Processing {len(notices)} notices")

        user_notices = defaultdict(list)
        for i, notice in enumerate(notices):
            user_notices[notice.status].append(notice)
            is_last_notice = len(notices) == (i + 1)
            is_next_user_different = (
                is_last_notice or notices[i + 1].user != notice.user
            )
            if is_last_notice or is_next_user_different:
                self.render_email(notice.user, user_notices)
                user_notices = defaultdict(list)
        self.send_all()
        notices.update(sent=True)

    def sample_email(self, email):
        """Return sample data to preview notification content"""
        self.stdout.write(f"Sending sample notifications to {email}")

        user = get_user_model().objects.create_user(
            f'Automation User', email, 'Sample Notifications'
        )
        try:
            notice_setting = NoticeSetting.objects.create(
                user=user, kind=NoticeSetting.REPORT_UPDATE_KIND
            )
            report_test_data = {
                "address": 'Augustastrasse 78, 52070 Aachen',
                'description': 'Test-Beschreibung',
                'geometry': Point(6.101_866_500_000_003, 50.773_345_280_000_01),
                'status_reason': '<Begründung der Ablehnung>',
                'number': 1,
                'user_id': user.id,
            }

            # Create an email with the singular variant of each block
            singular = defaultdict(list)
            for status in NOTIFICATION_STATUSES:
                singular[status].append(
                    StatusNotice.objects.create(
                        report=BikeStands.objects.create(
                            status=status, **report_test_data
                        ),
                        status=status,
                        user=user,
                    )
                )
            self.render_email(user, singular)

            # Create an email for variations of linked plannings
            plannings = defaultdict(list)
            for num_plannings in range(1, 3):
                plannings[Report.STATUS_REPORT_ACCEPTED].append(
                    StatusNotice.objects.create(
                        report=BikeStands.objects.create(
                            status=Report.STATUS_REPORT_ACCEPTED, **report_test_data
                        ),
                        status=Report.STATUS_REPORT_ACCEPTED,
                        user=user,
                    )
                )
                plannings[Report.STATUS_REPORT_ACCEPTED][-1].report.plannings.set(
                    [
                        BikeStands.objects.create(
                            status=Report.STATUS_PLANNING, **report_test_data
                        )
                        for i in range(num_plannings)
                    ]
                )
            self.render_email(user, plannings)

            # Create an email with the plural variant of each block
            plural = defaultdict(list)
            for status in NOTIFICATION_STATUSES:
                for i in range(3):
                    plural[status].append(
                        StatusNotice.objects.create(
                            report=BikeStands.objects.create(
                                status=status, **report_test_data
                            ),
                            status=status,
                            user=user,
                        )
                    )
            self.render_email(user, plural)
            self.send_all()
        finally:
            Report.objects.filter(user=user).delete()
            user.delete()

    def render_email(self, user, collection):
        """Render a collection of notices into a single email"""

        if StatusNotice.user_preference(user) == False:
            # user disabled notifications since notice was enqueued, delete
            # all notices for this user
            StatusNotice.objects.filter(user=user).delete()
            return

        unsubscribe_url = StatusNotice.unsubscribe_url(user).replace(
            "/api/", f"{settings.FRONTEND_URL}/api/v1/"
        )

        # Return early if collection contains no notices that will be included
        # in email
        total_in_collection = sum([len(collection[k]) for k in NOTIFICATION_STATUSES])
        if total_in_collection == 0:
            return

        data = self.template_data(collection)
        subject = "Neuigkeiten zu Ihren Radbügeln"
        body_txt = self.template_txt.render(
            context={"user": user, "unsubscribe_url": unsubscribe_url, **data}
        )
        body_html = self.template_html.render(
            context={"user": user, "unsubscribe_url": unsubscribe_url, **data}
        )
        self.email_data.append(
            (subject, body_txt, body_html, settings.DEFAULT_FROM_EMAIL, [user.email])
        )

    def send_all(self):
        connection = get_connection()
        messages = []
        for subject, text, html, from_email, recipient in self.email_data:
            message = EmailMultiAlternatives(subject, text, from_email, recipient)
            message.attach_alternative(html, 'text/html')
            if settings.EMAIL_REPLY_TO:
                message.reply_to = (settings.EMAIL_REPLY_TO,)
            messages.append(message)
        self.stdout.write(f"Sending {len(messages)} emails")
        return connection.send_messages(messages)

    def template_data(self, collection):
        """Shape data from a collection of notices so that it's ergonomic for templates"""

        data = {}
        for status in NOTIFICATION_STATUSES:
            if len(collection[status]) == 0:
                data[status] = None
            else:
                data[status] = dict()
                data[status]["is_single"] = len(collection[status]) == 1

                if len(collection[status]) == 1:
                    first = collection[status][0]
                    data[status]["first_address"] = first.report.address
                    data[status]["first_url"] = first.report.frontend_url
                    data[status]["first_reason"] = (
                        f": {first.report.status_reason}"
                        if (
                            first.report.status_reason
                            and len(first.report.status_reason) > 0
                        )
                        else "."
                    )
                data[status]["count"] = len(collection[status])
                data[status]["notices"] = collection[status]

        return data
