# """
# WSGI config for task_analyzer project.
# """

# import os

# from django.core.wsgi import get_wsgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'task_analyzer.settings')

# application = get_wsgi_application()

"""
WSGI config for task_analyzer project.
"""

import os
import sys  # Keep this import

from django.core.wsgi import get_wsgi_application

# CRITICAL VERCEL PATH FIX
# ------------------------------------------------------------------
# Add the 'backend' directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add the repository root directory (task-analyzer) to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# ------------------------------------------------------------------


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'task_analyzer.settings')

application = get_wsgi_application()