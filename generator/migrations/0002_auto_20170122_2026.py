# Generated by Django 2.0.dev20170120074947 on 2017-01-22 20:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('generator', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prime',
            name='number',
            field=models.BigIntegerField(),
        ),
    ]
