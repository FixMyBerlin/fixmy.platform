#!/usr/bin/env python
import os
import sys

from django.conf import settings

DEBUGPY_PORT = 3000

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fixmydjango.settings")

    if settings.DEBUG and os.environ.get("DEBUGPY") == "1":
        import debugpy

        try:
            debugpy.listen(("0.0.0.0", DEBUGPY_PORT))
            # debugpy.wait_for_client()
            sys.stdout.write(f'debugpy attached on {DEBUGPY_PORT}!\n')
        except RuntimeError:
            # debugpy cannot attach again when dev server is restarted
            pass

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    execute_from_command_line(sys.argv)
