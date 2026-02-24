"""
WSGI config for travel_system project.
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

# Add parent folder (project_root/travel_system) to sys.path so
# `travel_system.settings` resolves when project has nested layout.
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_system.settings')

application = get_wsgi_application()
