from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth.models import User
from django.http import HttpResponse
from .models import FeedSource, Label, FeedSourceLabel
from rest_framework import viewsets, permissions, generics
from .serializers import UserSerializer, FeedSourceSerializer, LabelSerializer, FeedSourceLabelSerializer, CreateFeedSourceLabelSerializer
from oauth2_provider.ext.rest_framework import TokenHasReadWriteScope, TokenHasScope
import requests
from django.views.decorators.csrf import csrf_exempt

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

class FeedSourceLabelSerializer(viewsets.ModelViewSet):
    queryset = FeedSourceLabel.objects.all()
    serializer_class = FeedSourceLabelSerializer

class CreateFeedSourceLabelView(viewsets.ModelViewSet):
    queryset = FeedSourceLabel.objects.all()
    serializer_class = CreateFeedSourceLabelSerializer

    def perform_create(self, serializer):
        serializer.save(user = self.request.user)

def proxy(request, url):
    req = requests.get(url)
    response = HttpResponse(req.text)
    return response
