# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-03 14:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feeds', '0005_remove_label_feedsources'),
    ]

    operations = [
        migrations.AddField(
            model_name='label',
            name='feedSources',
            field=models.ManyToManyField(to='feeds.FeedSource'),
        ),
    ]
