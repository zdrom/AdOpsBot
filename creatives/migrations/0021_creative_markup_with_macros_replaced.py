# Generated by Django 3.0.7 on 2020-08-03 16:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('creatives', '0020_remove_creative_markup_without_blocking_with_macros'),
    ]

    operations = [
        migrations.AddField(
            model_name='creative',
            name='markup_with_macros_replaced',
            field=models.TextField(blank=True),
        ),
    ]