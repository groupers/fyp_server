# Generated by Django 2.0.dev20170120074947 on 2017-02-28 19:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('popclick', '0006_auto_20170228_1941'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='auth',
            field=models.CharField(max_length=530),
        ),
    ]
