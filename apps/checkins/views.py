import datetime

from django.http import HttpResponseRedirect, HttpResponse,\
        HttpResponseNotFound, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.template import RequestContext
from django.contrib.contenttypes.models import ContentType

from django.views.generic.list_detail import object_list

from checkins.models import CheckIn
from olwidget.widgets import MapDisplay

#from vectorformats.Formats import Django, GeoJSON
from django.core import serializers

from django.contrib.auth.models import User


@login_required
def list(request, app_label=None, model_name=None, id=None, ):
    ''' List checkins for object

    '''

    try:
        ct = ContentType.objects.get(app_label=app_label, model= model_name)
        obj = ct.get_object_for_this_type(id=id)

    except:
        raise Http404

    checkins = CheckIn.objects.filter(content_type = ct, object_id = obj.id)

    paginator = Paginator(checkins, 1)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    # If page request (9999) is out of range, deliver last page of results.
    try:
        page = paginator.page(page)
    except (EmptyPage, InvalidPage):
        page = paginator.page(paginator.num_pages)


    return object_list( request,
            queryset = checkins,
            template_name = 'checkins/checkins_text_list.html',
            paginate_by=1,
            extra_context=locals(),
    )


@login_required
def detail(request, id):
    ''' Responds with the point and related object information

    '''

    try:
        point = Point.objects.get( id=id )

    except:
        return HttpResponseRedirect(reverse('points_list'))


    map = MapDisplay( fields = [ point.point, ],
            map_options = {
                    'map_style':{'width':'100%', 'height':'550px',},
            }
    )

    ct = ContentType.objects.get(\
            app_label = point.content_type.app_label,
            model = point.content_type.model)

    obj = ct.get_object_for_this_type(id = point.object_id)

    context = {'point':point, 'object':obj, 'content_type': ct, 'map':map,  }

    return render_to_response('points/detail.html', context,\
                context_instance=RequestContext(request))

@login_required
def delete(request, id):
    ''' can delete a point with a POST from the owner

    '''
    try:
        point = Point.objects.get(id=id)
    except:
        return HttpResponseNotFound()

    context = {'point':point,}
    if request.user == point.owner:

        if request.method == 'POST':
            point.delete()
            return HttpResponseNotFound()

        else:
            return render_to_response('points/confirm_delete.html', context,\
                    context_instance=RequestContext(request))

    else:
        return HttpResponseNotFound()

@login_required
def change(request, id):
    ''' Change the data for a single Point() obj '''

    try:
        point = Point.objects.get(id=id)
    except:
        return HttpResponseNotFound()

    if request.method == 'POST' and point.owner == request.user:

        form = PointForm(request.POST, instance=point)

        if form.is_valid():
            form.save()
            try:
                return HttpResponseRedirect(point.content_object.get_absolute_url())
            except:
                return HttpResponseRedirect(point.get_absolute_url())

    elif point.owner == request.user:
        form = PointForm( instance=point)
        context = {'point':point, 'form':form, }
        return render_to_response('points/change.html', context,\
                context_instance=RequestContext(request) )

    else:
        return HttpResponseNotFound()

@login_required
def add(request, app_label, model_name, id):
    '''add a checkin to the content_object for request.user now!

    The owner is request.user and
    the related obj is received from the url.
    '''
    try:
        ct = ContentType.objects.get(\
                app_label = app_label,
                model = model_name)
        obj = ct.get_object_for_this_type( id=id )

    except:
        return HttpResponseNotFound()

    if request.method == 'POST':
        try:
            c = CheckIn(owner=request.user, content_type = ct,
                    object_id = obj.id, content_object=obj,
            )
            c.save()

            try:
                return HttpResponseRedirect(obj.get_absolute_url())

            except:
                return HttpResponse('no get_absolute_url here')

        except:
            return HttpResponse(c.point)


    else:
        return render_to_response('add_checkin_solo.html', locals(),
                context_instance = RequestContext(request))

@login_required
def friends(request, username):
   user = get_object_or_404( User, username=username)
   friends = user.friends.all()

   checkins = CheckIn.objects.filter(owner__in=friends)

   return object_list(request,
           queryset=checkins,
    )

@login_required
def for_user(request, username):
    user = get_object_or_404(User, username=username)
    checkins = CheckIn.objects.filter(owner=user)

    return object_list(request,
            queryset=checkins,
    )

@login_required
def all(request):
    checkins = CheckIn.objects.filter(
            datetime__gte=datetime.datetime.now() -
            datetime.timedelta(hours=24),
            point__isnull=False
    )

    return object_list(request,
            queryset= checkins,
            extra_context = locals()
    )
