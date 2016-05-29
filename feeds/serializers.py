from django.contrib.auth.models import User
from rest_framework import serializers
from .models import FeedSource, Label, FeedSourceLabel


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email')

class FeedSourceSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = FeedSource
        fields = ('url', 'sourceUrl', 'name', 'user')

class LabelSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Label
        fields = ('url', 'name', 'user')

class FeedSourceLabelSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FeedSourceLabel
        fields = ('url', 'feedsource', 'label')
