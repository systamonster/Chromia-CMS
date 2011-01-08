from django.conf.urls.defaults import *
from django.conf import settings
from os.path import join

prefix = '/web/'
urlpatterns = patterns('',
    (r'^$', 'chromia.cms.views.get_path', {'template':'frontend/page.html', 'prefix':prefix}),
    (r'^(?P<path>.*)/$', 'chromia.cms.views.get_path', {'template':'frontend/page.html', 'prefix':prefix}),
    (r'^img/(.*)$', 'django.views.static.serve', {'document_root': join(settings.MEDIA_ROOT, 'frontend', 'img')}),
    (r'^css/(.*)$', 'django.views.static.serve', {'document_root': join(settings.MEDIA_ROOT, 'frontend', 'css')}),
)
