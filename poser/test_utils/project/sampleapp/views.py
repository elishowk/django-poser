# Create your views here.
from django.http import Http404
from django.shortcuts import render_to_response
from django.template.context import RequestContext

def sample_view(request, **kw):
    context = RequestContext(request, kw)
    return render_to_response("sampleapp/home.html", context)

def root(request, **kw):
    return sample_view(request, **kw)

def extra_view(request, **kw):
    context = RequestContext(request, kw)
    return render_to_response("sampleapp/extra.html", context)

def notfound(request):
    raise Http404
