# Generated by Django 3.0.7 on 2020-06-10 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('creatives', '0007_auto_20200610_1922'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creative',
            name='screenshot',
            field=models.ImageField(blank=True, upload_to='screenshots'),
        ),
    ]
