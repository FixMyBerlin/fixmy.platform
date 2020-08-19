#!/usr/bin/env python
import os
import sys

is_testing = 'test' in sys.argv

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fixmydjango.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    if is_testing:
        import coverage

        cov = coverage.coverage(source=['fixmyapp', 'survey'], omit=['*/tests/*'])
        cov.set_option('report:show_missing', True)
        cov.erase()
        cov.start()

    execute_from_command_line(sys.argv)

    if is_testing:
        cov.stop()
        cov.save()
