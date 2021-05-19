import sys
import dateutil.parser
from datetime import datetime, timezone
from django.conf import settings


def gastro_signups_open():
    """Return True if gastro signups are configured to be open.

    If the configuration options are not set, this defaults to True (open).

    If no valid date is set in the open and close env vars, this defaults to False"""
    if settings.GASTRO_SIGNUPS_OPEN == None or settings.GASTRO_SIGNUPS_CLOSE == None:
        return True

    try:
        start = dateutil.parser.parse(settings.GASTRO_SIGNUPS_OPEN).replace(
            tzinfo=timezone.utc
        )
        end = dateutil.parser.parse(settings.GASTRO_SIGNUPS_CLOSE).replace(
            tzinfo=timezone.utc
        )
    except dateutil.parser._parser.ParserError:
        # No explicit start and end times defined
        sys.stderr.write(
            'Error parsing gastro signup open and close times. Fallback to open.'
        )
        return False
    rv = start < datetime.now(tz=timezone.utc) < end
    return rv
