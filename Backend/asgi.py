"""
ASGI config for Backend project.

It exposes the ASGI callable as a module-level variable named ``application``.
"""

import os
import sys
from django.core.asgi import get_asgi_application

# 🔹 Add project root to path (important for deployment)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# 🔹 Set settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')

# 🔹 Create ASGI application
application = get_asgi_application()