#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # Ensure inner project package is on sys.path so imports like
    # `travel_system.settings` resolve when the repo has an extra
    # top-level `travel_system/` folder (project layout: travel_system/travel_system)
    project_root = os.path.dirname(__file__)
    sys.path.insert(0, os.path.join(project_root, 'travel_system'))

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_system.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
