from django.conf.urls.defaults import *

urlpatterns = patterns('hgscm.apps.www.views',
    url(r'^$', 'frontpage', name='frontpage'),
    url(r'^about$', 'about', name='about'),
    url(r'^workflow_guide$', 'workflow_guide', name='workflow_guide'),
    url(r'^thepage$', 'thepage', name='thepage'),
    url(r'^downloads$', 'downloads', name='downloads'),
    url(r'^download/(?P<version>.*?)/(?P<platform>.*?)$', 'download', name='download'),
)
