import os
import sys
sys.path.append('/var/www/PageLoadStatsPy')
sys.path.append('/var/www/PageLoadStatsPy/PageLoadStatsPy')
os.environ['DJANGO_SETTINGS_MODULE'] = 'PageLoadStatsPy.settings'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
