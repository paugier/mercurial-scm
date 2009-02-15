from django.conf.urls.defaults import *

urlpatterns = patterns('hgscm.apps.www.views',
    url(r'^$', 'frontpage', name='frontpage'),
)