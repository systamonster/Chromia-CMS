#/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import os.path

sys.path.insert(0, os.path.dirname(__file__))
os.environ['DJANGO_SETTINGS_MODULE'] = 'chromia.settings'

from django.core.handlers.wsgi import WSGIHandler
application = WSGIHandler()

