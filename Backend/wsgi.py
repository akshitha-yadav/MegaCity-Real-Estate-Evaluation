"""
WSGI config for Backend project.

It exposes the WSGI callable as a module-level variable named ``application``.
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

# 🔹 Add project root to Python path (important for deployment)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# 🔹 Set default settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')

# 🔹 Initialize WSGI application
application = get_wsgi_application()