# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-28 15:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('popclick', '0003_auto_20170312_1200'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile_PO_InterestDistance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('po_distance', models.DecimalField(decimal_places=9, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('interest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='popclick.Interest')),
                ('pageobject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='popclick.PageObject')),
            ],
        ),
        migrations.CreateModel(
            name='Profile_PO_Ticket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='popclick.Page')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='popclick.Profile')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='pageinterest',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='pageinterest',
            name='interest',
        ),
        migrations.RemoveField(
            model_name='pageinterest',
            name='page',
        ),
        migrations.AlterUniqueTogether(
            name='pageobjectinterest',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='pageobjectinterest',
            name='interest',
        ),
        migrations.RemoveField(
            model_name='pageobjectinterest',
            name='pageobject',
        ),
        migrations.DeleteModel(
            name='PageInterest',
        ),
        migrations.DeleteModel(
            name='PageobjectInterest',
        ),
        migrations.AddField(
            model_name='profile_po_interestdistance',
            name='ticket',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='popclick.Profile_PO_Ticket'),
        ),
        migrations.AlterUniqueTogether(
            name='profile_po_interestdistance',
            unique_together=set([('ticket', 'pageobject', 'interest')]),
        ),
    ]