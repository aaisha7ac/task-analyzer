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
import sys

from django.core.wsgi import get_wsgi_application

# CRITICAL VERCEL PATH FIX (Universal Approach)
# ------------------------------------------------------------------
# Get the absolute path of the directory containing wsgi.py (task_analyzer)
current_dir = os.path.dirname(os.path.abspath(__file__))

# 1. Add the "backend" directory to the path. (Up one level from task_analyzer)
backend_dir = os.path.join(current_dir, '..')
sys.path.append(backend_dir)

# 2. Add the repository root directory (task-analyzer) to the path. (Up two levels)
repo_root = os.path.join(current_dir, '..', '..')
sys.path.append(repo_root)

# ------------------------------------------------------------------

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'task_analyzer.settings')

application = get_wsgi_application()