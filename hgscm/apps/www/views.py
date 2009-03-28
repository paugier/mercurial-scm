from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.utils import simplejson
from django.conf import settings
from hgscm.apps.www.models import get_download, get_latest_version
import os

def frontpage(request):
    return render_to_response("frontpage.html", { },
        RequestContext(request))
def about(request):
    return render_to_response("about.html", { },
        RequestContext(request))
def thepage(request):
    return render_to_response("thepage.html", { },
        RequestContext(request))
def download(request, platform, version):
    return HttpResponseRedirect(get_download(platform, version)['url'])
def downloads(request):
    f = open(os.path.join(settings.MEDIA_ROOT, "downloads.json"))
    list = simplejson.load(f)
    f.close()
    return render_to_response("downloads.html", {'downloads': list},
        RequestContext(request))
