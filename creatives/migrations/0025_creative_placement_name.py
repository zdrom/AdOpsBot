# Generated by Django 3.0.7 on 2021-12-14 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('creatives', '0024_auto_20211213_1840'),
    ]

    operations = [
        migrations.AddField(
            model_name='creative',
            name='placement_name',
            field=models.CharField(blank=True, max_length=500),
        ),
    ]
