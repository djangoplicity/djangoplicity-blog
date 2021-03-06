# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-03-17 18:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0006_post_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='footer_en',
            field=models.TextField(blank=True, help_text='Optional footer added to the bottom of posts', null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='footer_es',
            field=models.TextField(blank=True, help_text='Optional footer added to the bottom of posts', null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='name_en',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='name_es',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='slug_en',
            field=models.SlugField(help_text='Slug of the category, used for URLs', null=True, unique=True),
        ),
        migrations.AddField(
            model_name='category',
            name='slug_es',
            field=models.SlugField(help_text='Slug of the category, used for URLs', null=True, unique=True),
        ),
    ]
