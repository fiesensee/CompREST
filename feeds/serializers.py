from django.contrib.auth.models import User
from rest_framework import serializers
from .models import FeedSource, Label, FeedSourceLabel


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class FeedSourceSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = FeedSource
        fields = ('url', 'id', 'sourceUrl', 'name', 'user')

class LabelSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    feedSources = FeedSourceSerializer(many = True, read_only = True)


    class Meta:
        model = Label
        fields = ('url', 'id', 'name', 'feedSources', 'user')


class FeedSourceLabelSerializer(serializers.Serializer):

    # def __init__(self, *args, **kwargs):
    #     many = kwargs.pop('many', True)
    #     super(FeedSourceLabelSerializer, self).__init__(many=many, *args, **kwargs)

    # feedSource = serializers.HyperlinkedRelatedField(view_name="feedsource-detail", queryset = FeedSource.objects.all())
    label = serializers.HyperlinkedRelatedField(view_name="label-detail", queryset = Label.objects.all())
    user = serializers.ReadOnlyField(source='user.username')
    # feedSources = serializers.ListField(child = serializers.HyperlinkedRelatedField(view_name='feedSource-detail', queryset = FeedSource.objects.all()))

    # def create(self, validated_data):
    #
