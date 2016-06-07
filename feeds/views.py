from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth.models import User
from django.http import HttpResponse
from .models import FeedSource, Label, FeedSourceLabel
from rest_framework import viewsets, permissions, generics
from .serializers import UserSerializer, FeedSourceSerializer, LabelSerializer, FeedSourceLabelSerializer
from oauth2_provider.ext.rest_framework import TokenHasReadWriteScope, TokenHasScope
from oauth2_provider.decorators import protected_resource
import json, feedparser, pytz
import datetime
import time
from django.views.decorators.csrf import csrf_exempt
from oauth2_provider.views.generic import ProtectedResourceView

class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

class FeedSourceViewSet(viewsets.ModelViewSet):
    queryset = FeedSource.objects.all()
    serializer_class = FeedSourceSerializer

    def perform_create(self, serializer):
        serializer.save(user = self.request.user)

class LabelViewSet(viewsets.ModelViewSet):
    queryset = Label.objects.all()
    serializer_class = LabelSerializer

    def perform_create(self, serializer):
        serializer.save(user = self.request.user)

class FeedSourceLabelViewSet(viewsets.ModelViewSet):
    queryset = FeedSourceLabel.objects.all()
    serializer_class = FeedSourceLabelSerializer

class CreateFeedSourceLabels(ProtectedResourceView):

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        super(CreateFeedSourceLabels, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        joins = json.loads(request.body)
        print joins
        for join in joins:
            label = Label.objects.get(pk = join['labelId'])
            feedSourceIds = join['feedSourceIds']
            joinObjects = FeedSourceLabel.objects.filter(label = label)
            joinObjects.delete()
            for feedSourceId in feedSourceIds:
                feedSource = FeedSource.objects.get(pk = feedSourceId)
                FeedSourceLabel.objects.create(label = label, feedSource = feedSource, user = self.request.user)

def proxy(request, url):
    feeds = []
    source = feedparser.parse(url)
    defaultText = 'undefined'
    defaultDate = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    utc = pytz.utc
    berlin = pytz.timezone('Europe/Berlin')
    for entry in source['items']:
        feed = {
            'title':defaultText,
            'description':defaultText,
            'link':defaultText,
            'date':defaultDate
        }
        if('title' in entry):
            feed['title'] = entry['title']
        if('description' in entry):
            feed['description'] = entry['description']
        if('link' in entry):
            feed['link'] = entry['link']
        if('published_parsed' in entry):
            date = datetime.datetime.fromtimestamp(time.mktime(entry['published_parsed']))
            utcDate = utc.localize(date)
            feed['date'] = utcDate.astimezone(berlin).strftime("%d-%m-%Y %H:%M:%S")
        feeds.append(feed)

    response = HttpResponse(json.dumps(feeds))
    return response
