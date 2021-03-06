# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-31 13:46
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('popclick', '0004_auto_20170328_1522'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProfileVirtualInterest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.IntegerField(default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('interest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='popclick.Interest')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='popclick.Profile')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='profilevirtualinterest',
            unique_together=set([('profile', 'interest')]),
        ),
    ]
