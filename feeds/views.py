from django.shortcuts import render
from django.contrib.auth.models import User
from .models import FeedSource, Label, FeedSourceLabel
from rest_framework import viewsets, permissions
from .serializers import UserSerializer, FeedSourceSerializer, LabelSerializer, FeedSourceLabelSerializer
from oauth2_provider.ext.rest_framework import TokenHasReadWriteScope, TokenHasScope

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
