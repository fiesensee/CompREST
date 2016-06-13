from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views.generic import View
from .models import FeedSource, Label, FeedSourceLabel, RefreshService
from rest_framework import viewsets, permissions, generics, mixins
from .serializers import UserSerializer, FeedSourceSerializer, LabelSerializer, FeedSourceLabelSerializer
from oauth2_provider.ext.rest_framework import TokenHasReadWriteScope, TokenHasScope
from oauth2_provider.decorators import protected_resource
import json, feedparser, pytz, hashlib, base64
import datetime
import time
from threading import Timer
from django.views.decorators.csrf import csrf_exempt
from oauth2_provider.views.generic import ProtectedResourceView
from pyelasticsearch import ElasticSearch

class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class FeedSourceViewSet(viewsets.ModelViewSet):
    queryset = FeedSource.objects.all()
    serializer_class = FeedSourceSerializer

    def perform_create(self, serializer):
        serializer.save(user = self.request.user)

    def get_queryset(self):
        user = self.request.user
        return FeedSource.objects.filter(user=user)


class LabelViewSet(viewsets.ModelViewSet):
    queryset = Label.objects.all()
    serializer_class = LabelSerializer

    def perform_create(self, serializer):
        serializer.save(user = self.request.user)

    def get_queryset(self):
        user = self.request.user
        return Label.objects.filter(user=user)

class FeedSourceLabelViewSet(viewsets.ModelViewSet):
    queryset = FeedSourceLabel.objects.all()
    serializer_class = FeedSourceLabelSerializer

    def get_queryset(self):
        user = self.request.user
        return FeedSourceLabel.objects.filter(user=user)

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

def resetService(request):
    service = RefreshService.objects.first()
    service.running = False
    service.save()
    response = HttpResponse()
    response.status_code = 200
    return response

def activateClient(request):
    service = RefreshService.objects.first()
    if(service is None):
        service = RefreshService.objects.create()
    service.clientActive = True
    service.save()

    print "activated"
    print (service.running)
    if(service.running is False):
        print "start service"
        refresh(service)
        timer = Timer(60*30, inactivate, [service])
        timer.start()

    response = HttpResponse()
    response.status_code = 200
    return response

def inactivate(service):
    print "stopping service"
    service.clientActive = False
    service.running = False
    service.save()


def refresh(service):
    print "check clientActive"
    service.running = True
    service.save()
    timer = Timer(60*5, refresh, [service])
    if(service.clientActive):
        print "start refresh"
        timer.start()
        getFeeds()

@csrf_exempt
def getFeeds():
    print "refreshing"
    es = ElasticSearch('http://fisensee.ddns.net:9200/')

    query = {"query": {"range": {"date": {"lte": "now-1M/M"}}}}
    oldFeeds = es.search(query, size=300, index='feeds')
    print es.search(query, size=300, index='feeds')

    if(len(oldFeeds['hits']['hits']) is not 0):
        es.bulk(es.delete_op(id=feed['_id'], index='feeds',
        doc_type='feed') for feed in oldFeeds['hits']['hits'])


    feedSources = FeedSource.objects.all()
    feeds = []
    defaultText = 'undefined'
    # urls = json.loads(request.body)
    defaultDate = datetime.datetime.now().isoformat()
    utc = pytz.utc
    berlin = pytz.timezone('Europe/Berlin')
    now = datetime.datetime.today()
    dateThreshold = now - datetime.timedelta(weeks=8)

    allUrls = []
    for feedSource in feedSources:
        print feedSource.sourceUrl
        allUrls.append(feedSource.sourceUrl)

    urls = set(allUrls)
    print str(urls)
    for url in urls:
        source = feedparser.parse(url)
        for entry in source['items']:
            feed = {
                'title':defaultText,
                'description':defaultText,
                'link':defaultText,
                'date':defaultDate,
                'url': defaultText
            }
            if('title' in entry):
                feed['title'] = entry['title']
            if('description' in entry):
                feed['description'] = entry['description']
            if('link' in entry):
                feed['link'] = entry['link']
            if('published_parsed' in entry):
                date = datetime.datetime.fromtimestamp(time.mktime(entry['published_parsed']))
                if(date < dateThreshold):
                    break
                utcDate = utc.localize(date)
                feed['date'] = utcDate.astimezone(berlin).isoformat()
            #id creation should be enough for now, but it's made to fail
            if('title' or 'published_parsed' in entry):
                feed['id'] = base64.urlsafe_b64encode(hashlib.sha256((feed['title'] + feed['date']).encode('utf8')).hexdigest())
            else:
                feed['id'] = base64.urlsafe_b64encode(hashlib.sha256((feed['title']).encode('utf8')).hexdigest())
            feed['url'] = url
            feeds.append(feed)



    feedJson = json.dumps(feeds)
    es.bulk((es.index_op(feed) for feed in feeds),
        index = 'feeds',
        doc_type = 'feed')
    print es.refresh('feeds')
    response = HttpResponse()
    response.status_code = 201
    return response
