# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-04-10 00:52
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0004_auto_20180410_0051'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Options',
            new_name='Option',
        ),
    ]
