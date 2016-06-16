from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views.generic import View
from .models import FeedSource, Label, FeedSourceLabel, RefreshService
from rest_framework import viewsets, permissions, generics, mixins
from .serializers import UserSerializer, FeedSourceSerializer, LabelSerializer, FeedSourceLabelSerializer
from oauth2_provider.ext.rest_framework import TokenHasReadWriteScope, TokenHasScope
from oauth2_provider.decorators import protected_resource
import time, timer, json
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

        response = HttpResponse()
        response.status_code = 201
        return response


class Refresher(View):

    def get(self, request):
        timer.restartTimer()

        response = HttpResponse()
        response.status_code = 200
        return response
