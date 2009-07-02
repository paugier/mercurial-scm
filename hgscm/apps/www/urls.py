from django.conf.urls.defaults import *

urlpatterns = patterns('hgscm.apps.www.views',
    url(r'^$', 'frontpage', name='frontpage'),
    url(r'^about$', 'about', name='about'),
    url(r'^workflow-guide$', 'workflow_guide', name='workflow_guide'),
    url(r'^learn-mercurial$', 'learn_mercurial', name='learn_mercurial'),
    url(r'^quick-start$', 'quick_start', name='quick_start'),
    url(r'^who-uses-mercurial$', 'who_uses', name='who_uses'),
    url(r'^thepage$', 'thepage', name='thepage'),
    url(r'^downloads$', 'downloads', name='downloads'),
    url(r'^download/(?P<version>.*?)/(?P<platform>.*?)$', 'download', name='download'),
)
