from django.shortcuts import render_to_response
from django.template import RequestContext

def frontpage(request):
    return render_to_response("frontpage.html", { },
        RequestContext(request))
