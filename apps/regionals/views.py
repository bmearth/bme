from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.conf import settings

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

try:
    from friends.models import Friendship
    friends = True
except ImportError:
    friends = False

try:
    from threadedcomments.models import ThreadedComment
    forums = True
except ImportError:
    forums = False

try:
    from wiki.models import Article
    from wiki.views import get_ct
    wiki = True
except ImportError:
    wiki = False

from regionals.models import Regional
from regionals.forms import *
from microblogging.models import TweetInstance

TOPIC_COUNT_SQL = """
SELECT COUNT(*)
FROM regionals_topic
WHERE regionals_topic.regional_id = regionals_regional.id
"""
MEMBER_COUNT_SQL = """
SELECT COUNT(*)
FROM regionals_regional_members
WHERE regionals_regional_members.regional_id = regionals_regional.id
"""

from schedule.models import Calendar, CalendarRelation

def create(request, form_class=RegionalForm, template_name="regionals/create.html"):
    if request.user.is_authenticated() and request.method == "POST":
        if request.POST["action"] == "create":
            regional_form = form_class(request.POST)
            if regional_form.is_valid():
                regional = regional_form.save(commit=False)
                regional.creator = request.user
                regional.save()
                regional.members.add(request.user)
                regional.save()
                # @@@ this is just temporary to give regionals a single calendar -- will revisit during whole
                # regional/project merge effort
                calendar = Calendar(name = "%s Calendar" % regional.name)
                calendar.save()
                CalendarRelation.objects.create_relation(calendar, regional, distinction="default", inheritable=True)
                if notification:
                    # @@@ might be worth having a shortcut for sending to all users
                    notification.send(User.objects.all(), "regionals_new_regional", {"regional": regional}, queue=True)
                    if friends: # @@@ might be worth having a shortcut for sending to all friends
                        notification.send((x['friend'] for x in Friendship.objects.friends_for_user(regional.creator)), "regionals_friend_regional", {"regional": regional})
                #return render_to_response("base.html", {
                #}, context_instance=RequestContext(request))
                return HttpResponseRedirect(regional.get_absolute_url())
        else:
            regional_form = form_class()
    else:
        regional_form = form_class()
    
    return render_to_response(template_name, {
        "regional_form": regional_form,
    }, context_instance=RequestContext(request))

def regionals(request, template_name="regionals/regionals.html", order=None):
    regionals = Regional.objects.filter(deleted=False)
    search_terms = request.GET.get('search', '')
    if search_terms:
        regionals = (regionals.filter(name__icontains=search_terms) |
            regionals.filter(description__icontains=search_terms))
    if order == 'least_topics':
        regionals = regionals.extra(select={'topic_count': TOPIC_COUNT_SQL})
        regionals = regionals.order_by('topic_count')
    elif order == 'most_topics':
        regionals = regionals.extra(select={'topic_count': TOPIC_COUNT_SQL})
        regionals = regionals.order_by('-topic_count')
    elif order == 'least_members':
        regionals = regionals.extra(select={'member_count': MEMBER_COUNT_SQL})
        regionals = regionals.order_by('member_count')
    elif order == 'most_members':
        regionals = regionals.extra(select={'member_count': MEMBER_COUNT_SQL})
        regionals = regionals.order_by('-member_count')
    elif order == 'name_ascending':
        regionals = regionals.order_by('name')
    elif order == 'name_descending':
        regionals = regionals.order_by('-name')
    elif order == 'date_oldest':
        regionals = regionals.order_by('-created')
    elif order == 'date_newest':
        regionals = regionals.order_by('created')
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

def delete(request, slug, redirect_url=None):
    regional = get_object_or_404(Regional, slug=slug)
    if not redirect_url:
        redirect_url = reverse('regional_list')
    
    # @@@ eventually, we'll remove restriction that regional.creator can't leave regional but we'll still require regional.members.all().count() == 1
    if request.user.is_authenticated() and request.method == "POST" and request.user == regional.creator and regional.members.all().count() == 1:
        regional.deleted = True
        regional.save()
        request.user.message_set.create(message="Regional %s deleted." % regional)
        # @@@ no notification as the deleter must be the only member
    
    return HttpResponseRedirect(redirect_url)


def your_regionals(request, template_name="regionals/your_regionals.html"):
    return render_to_response(template_name, {
        "regionals": Regional.objects.filter(deleted=False, members=request.user).order_by("name"),
    }, context_instance=RequestContext(request))
your_regionals = login_required(your_regionals)

def regional(request, slug, form_class=RegionalUpdateForm,
        template_name="regionals/regional.html"):
    regional = get_object_or_404(Regional, slug=slug)

    if regional.deleted:
        raise Http404
    
    photos = regional.photos.all()
    
    if request.user.is_authenticated() and request.method == "POST":
        if request.POST["action"] == "update" and request.user == regional.creator:
            regional_form = form_class(request.POST, instance=regional)
            if regional_form.is_valid():
                regional = regional_form.save()
        else:
            regional_form = form_class(instance=regional)
        if request.POST["action"] == "join":
            regional.members.add(request.user)
            request.user.message_set.create(message="You have joined the regional %s" % regional.name)
            if notification:
                notification.send([regional.creator], "regionals_created_new_member", {"user": request.user, "regional": regional})
                notification.send(regional.members.all(), "regionals_new_member", {"user": request.user, "regional": regional})
                if friends: # @@@ might be worth having a shortcut for sending to all friends
                    notification.send((x['friend'] for x in Friendship.objects.friends_for_user(request.user)), "regionals_friend_joined", {"user": request.user, "regional": regional})
        elif request.POST["action"] == "leave":
            regional.members.remove(request.user)
            request.user.message_set.create(message="You have left the regional %s" % regional.name)
            if notification:
                pass # @@@
    else:
        regional_form = form_class(instance=regional)
    
    topics = regional.topics.all()[:5]
    articles = Article.objects.filter(
        content_type=get_ct(regional),
        object_id=regional.id).order_by('-last_update')
    total_articles = articles.count()
    articles = articles[:5]
    
    tweets = TweetInstance.objects.tweets_for(regional).order_by("-sent")
    
    are_member = request.user in regional.members.all()
    
    return render_to_response(template_name, {
        "regional_form": regional_form,
        "regional": regional,
        "photos": photos,
        "topics": topics,
        "articles": articles,
        "tweets": tweets,
        "total_articles": total_articles,
        "are_member": are_member,
    }, context_instance=RequestContext(request))

def topics(request, slug, form_class=TopicForm,
        template_name="regionals/topics.html"):
    regional = get_object_or_404(Regional, slug=slug)
    
    if regional.deleted:
        raise Http404
    
    are_member = False
    if request.user.is_authenticated():
        are_member = request.user in regional.members.all()
    
    if request.method == "POST":
        if request.user.is_authenticated():
            if are_member:
                topic_form = form_class(request.POST)
                if topic_form.is_valid():
                    topic = topic_form.save(commit=False)
                    topic.regional = regional
                    topic.creator = request.user
                    topic.save()
                    request.user.message_set.create(message="You have started the topic %s" % topic.title)
                    if notification:
                        notification.send(regional.members.all(), "regionals_new_topic", {"topic": topic})
                    topic_form = form_class() # @@@ is this the right way to reset it?
            else:
                request.user.message_set.create(message="You are not a member and so cannot start a new topic")
                topic_form = form_class()
        else:
            return HttpResponseForbidden()
    else:
        topic_form = form_class()
    
    return render_to_response(template_name, {
        "regional": regional,
        "topic_form": topic_form,
        "are_member": are_member,
    }, context_instance=RequestContext(request))

def topic(request, id, edit=False, template_name="regionals/topic.html"):
    topic = get_object_or_404(Topic, id=id)
    
    if topic.regional.deleted:
        raise Http404
    
    if request.method == "POST" and edit == True and \
        (request.user == topic.creator or request.user == topic.regional.creator):
        topic.body = request.POST["body"]
        topic.save()
        return HttpResponseRedirect(reverse('regional_topic', args=[topic.id]))
    return render_to_response(template_name, {
        'topic': topic,
        'edit': edit,
    }, context_instance=RequestContext(request))

def topic_delete(request, pk):
    topic = Topic.objects.get(pk=pk)
    
    if topic.regional.deleted:
        raise Http404
    
    if request.method == "POST" and (request.user == topic.creator or \
        request.user == topic.regional.creator): 
        if forums:
            ThreadedComment.objects.all_for_object(topic).delete()
        topic.delete()
    
    return HttpResponseRedirect(request.POST["next"])

