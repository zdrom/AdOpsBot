# Generated by Django 3.0.7 on 2020-08-03 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('creatives', '0018_creative_markup_with_macros'),
    ]

    operations = [
        migrations.AddField(
            model_name='creative',
            name='markup_without_blocking_with_macros',
            field=models.TextField(blank=True),
        ),
    ]