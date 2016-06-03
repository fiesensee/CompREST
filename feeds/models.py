from __future__ import unicode_literals
from django.contrib.auth.models import User

from django.db import models

class FeedSource(models.Model):

    name = models.CharField(max_length = 100)
    sourceUrl = models.CharField(max_length = 200)
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User)
    class Meta:
        ordering = ('created',)

class Label(models.Model):

    name = models.CharField(max_length = 100)
    created = models.DateTimeField(auto_now_add = True)
    user = models.ForeignKey(User)

    class Meta:
        ordering = ('created',)

class FeedSourceLabel(models.Model):

    label = models.ForeignKey(Label)
    feedsource = models.ForeignKey(FeedSource)
    user = models.ForeignKey(User)
