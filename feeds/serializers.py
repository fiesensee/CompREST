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
        fields = ('url', 'id', 'sourceUrl', 'name', 'user')

class LabelSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    feedSources = FeedSourceSerializer(many = True, read_only = True)


    class Meta:
        model = Label
        fields = ('url', 'name', 'feedSources', 'user')


class createAndUpdateLabelSerializer(serializers.Serializer):
    user = serializers.ReadOnlyField(source = 'user.username')
    name = serializers.CharField(max_length = 100)
    feedSourceQuery = FeedSource.objects.all()
    feedSources = serializers.ListField(
        # child = serializers.PrimaryKeyRelatedField(many = True, queryset = feedSourceQuery),
        allow_null = True
    )


    def create(self, validated_data):
        label = Label()
        label.name = validated_data.get('name')
        label.user = validated_data.get('user')
        label.save()
        self.setFeedSourceLabels(label, validated_data.get('feedSources'))
        return label


    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.user = validated_data.get('user', instance.user)
        feedSourceUrls = validated_data.get('feedSources')
        self.setFeedSourceLabels(label, validated_data.get('feedSources'))
        return label

    def setFeedSourceLabels(self, label, ids):
        for sourceId in ids:
            feedSourceObject = FeedSource.objects.get(pk=sourceId['id'])
            FeedSourceLabel.objects.create(label = label, feedsource = feedSourceObject)

    def deleteFeedSourceLabels(self, label, ids):
        for sourceId in ids:
            feedSource = FeedSource.objects.get(pk = sourceId.id)
            feedSourceLabel = FeedSourceLabel.objects.get(label = label, feedsource = feedSource)
            feedSourceLable.delete()



class FeedSourceLabelSerializer(serializers.HyperlinkedModelSerializer):
    feedsource = FeedSourceSerializer(read_only = True)
    label = LabelSerializer(read_only = True)
    user = serializers.ReadOnlyField(source='user.username')


    class Meta:
        model = FeedSourceLabel
        fields = ('url', 'feedsource', 'label', 'user')

class CreateFeedSourceLabelSerializer(serializers.HyperlinkedModelSerializer):
    feedsource = serializers.HyperlinkedRelatedField(view_name="feedsource-detail", queryset = FeedSource.objects.all())
    label = serializers.HyperlinkedRelatedField(view_name="label-detail", queryset = Label.objects.all())
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = FeedSourceLabel
        fields = ('url', 'feedsource', 'label', 'user')
