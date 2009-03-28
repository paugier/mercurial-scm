import os
from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
    (r'^', include('hgscm.apps.www.urls')),

    (r'^media/(?P<path>.*)$', 'django.views.static.serve', 
        { 'document_root': os.path.join(settings.MEDIA_ROOT) }),

    (r'^favicon\.ico$', 'django.views.static.serve', {'document_root': os.path.join(settings.MEDIA_ROOT), 'path': 'images/favicon.ico'}),
    # Uncomment the next line to enable the admin:
    # (r'^admin/(.*)', admin.site.root),
)
