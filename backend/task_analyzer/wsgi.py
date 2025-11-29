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

# CRITICAL FIX FOR VERCEL: Path Manipulation
# This calculates the path to the repository root (task-analyzer) and adds it to the system path.
# This ensures Python can find all your applications and modules (like the 'backend' folder).
# os.path.dirname(__file__) is the directory containing wsgi.py (task_analyzer)
# os.path.abspath(...) gets the absolute path
# join(..., '..', '..') goes up two levels to the repository root.
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.append(repo_root)

# If your 'backend' folder contains other necessary modules to import at the top level, 
# you should also include the 'backend' folder path:
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(backend_path)


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'task_analyzer.settings')

application = get_wsgi_application()