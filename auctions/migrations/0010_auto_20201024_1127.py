# Generated by Django 3.1.2 on 2020-10-24 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0009_auto_20201023_1956'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='closed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='listing',
            name='winner_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
