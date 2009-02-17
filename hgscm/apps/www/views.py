from django.shortcuts import render_to_response
from django.template import RequestContext

def frontpage(request):
    return render_to_response("frontpage.html", { },
        RequestContext(request))
def about(request):
    return render_to_response("about.html", { },
        RequestContext(request))
