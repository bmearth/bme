from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.conf import settings

from regionals.models import Regional

def regionals(request, template_name="regionals/regionals.html", order=None):
    regionals = Regional.objects.filter(deleted=False)
    search_terms = request.GET.get('search', '')
    if search_terms:
        regionals = (regionals.filter(name__icontains=search_terms) |
            regionals.filter(description__icontains=search_terms))
    context = {
        'regionals': regionals,
        'search_terms': search_terms,
        'order': order,
    }
    return render_to_response(
        template_name,
        context,
        context_instance=RequestContext(request)
    )
