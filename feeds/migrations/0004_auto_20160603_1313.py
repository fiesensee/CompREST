# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-03 13:13
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feeds', '0003_auto_20160603_1307'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='feedsource',
            name='url',
        ),
        migrations.RemoveField(
            model_name='label',
            name='url',
        ),
    ]
