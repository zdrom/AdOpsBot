# Generated by Django 3.0.7 on 2020-07-21 13:02

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('creatives', '0013_auto_20200717_1752'),
    ]

    operations = [
        migrations.AddField(
            model_name='creative',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2020, 7, 21, 13, 2, 30, 711195, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='creative',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
