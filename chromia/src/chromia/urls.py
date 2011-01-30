#
# Copyright (C) 2011 Kirill Gordeev <kirill.gordeev@gmail.com>
# Copyright (C) 2011 David Criado <dccirujeda@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

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
    (r'$', 'chromia.cms.views.redirect_main'),
)

