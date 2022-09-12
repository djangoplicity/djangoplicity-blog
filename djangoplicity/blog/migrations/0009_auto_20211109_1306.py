# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-11-09 13:06
from __future__ import unicode_literals

from django.db import migrations, models
import djangoplicity.blog.validators


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0008_auto_20210318_1740'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='body',
            field=models.TextField(validators=[djangoplicity.blog.validators.validate_string_template]),
        ),
    ]
