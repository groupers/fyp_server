# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-03 15:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('popclick', '0005_auto_20170331_1346'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interest',
            name='name',
            field=models.CharField(max_length=200, primary_key=True, serialize=False, unique=True),
        ),
    ]