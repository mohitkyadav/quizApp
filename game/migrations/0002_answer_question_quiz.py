# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-04-09 08:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=128, verbose_name=b"Answer's text here.")),
                ('correct', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.CharField(max_length=128, verbose_name=b'Enter question here.')),
                ('is_final', models.BooleanField(default=False)),
                ('answers', models.ManyToManyField(to='game.Answer')),
            ],
        ),
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name=b'Name of exam')),
                ('slug', models.SlugField(max_length=64, unique=True)),
                ('questions', models.ManyToManyField(to='game.Question')),
            ],
        ),
    ]
