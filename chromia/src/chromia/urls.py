from django.conf.urls.defaults import *
from django.conf import settings
from os.path import join

# Uncomment the next two lines to enable the admin:

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    (r'^chromia/admin/(.*)', admin.site.root),
    # (r'^chromia/admin/', include('django.contrib.admin.urls')),
    (r'^images/(.*)$', 'django.views.static.serve', {'document_root': join(settings.MEDIA_ROOT, 'images')}),
    (r'^web/redirect', 'chromia.cms.views.redirect_external'),
    (r'^web/', include('chromia.web_urls')),
)

