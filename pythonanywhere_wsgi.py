# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# PythonAnywhere WSGI configuration file for Flashcards REST API
#
# Instructions:
# 1. On PythonAnywhere, go to the "Web" tab.
# 2. Click "Add a new web app" -> choose "Manual configuration" -> select Python 3.11, 3.12, or 3.13.
# 3. In the "Code" section:
#      Source code: /home/<YOUR_USERNAME>/Flash-cards/backend
#      Working directory: /home/<YOUR_USERNAME>/Flash-cards/backend
# 4. In the "Virtualenv" section:
#      Path to your virtualenv, e.g. /home/<YOUR_USERNAME>/.virtualenvs/flashcards-env
# 5. Click on the "WSGI configuration file" link.
# 6. Delete all default code in that file, copy and paste the code below,
#    and replace '<YOUR_USERNAME>' with your actual PythonAnywhere username!
# 7. In "Static files" section:
#      URL: /static/
#      Directory: /home/<YOUR_USERNAME>/Flash-cards/backend/staticfiles
# 8. Click the green "Reload <YOUR_USERNAME>.pythonanywhere.com" button at the top!
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import os
import sys

# 1. Path to your backend directory
# REPLACE '<YOUR_USERNAME>' with your PythonAnywhere username:
USERNAME = '<YOUR_USERNAME>'
project_home = f'/home/{USERNAME}/Flash-cards/backend'

if project_home not in sys.path:
    sys.path.insert(0, project_home)

# 2. Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

# Optional environment overrides (can also be loaded from backend/.env):
# os.environ['DEBUG'] = 'False'
# os.environ['SECRET_KEY'] = 'replace-with-a-secure-random-key'
# os.environ['ALLOWED_HOSTS'] = '*'
# os.environ['CORS_ALLOW_ALL_ORIGINS'] = 'True'
# os.environ['DATABASE_URL'] = '...' # If using Postgres/MySQL, otherwise SQLite is used automatically!

# 3. Serve through WSGI
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
