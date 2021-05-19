import sys
import dateutil.parser
from datetime import datetime, timezone
from django.conf import settings


def gastro_signups_open():
    """Return True if gastro signups are configured to be open."""
    if settings.TOGGLE_GASTRO_SIGNUPS in [True, False]:
        return settings.TOGGLE_GASTRO_SIGNUPS

    try:
        start = dateutil.parser.parse(settings.GASTRO_SIGNUPS_OPEN).replace(
            tzinfo=timezone.utc
        )
        end = dateutil.parser.parse(settings.GASTRO_SIGNUPS_CLOSE).replace(
            tzinfo=timezone.utc
        )
    except TypeError:
        # No explicit start and end times defined
        sys.stderr.write(
            'Error parsing gastro signup open and close times. Fallback to open.'
        )
        return True
    rv = start < datetime.now(tz=timezone.utc) < end
    return rv
