# Generated by Django 3.0.7 on 2020-06-15 22:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('creative_groups', '0003_auto_20200615_2156'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creativegroup',
            name='name',
            field=models.CharField(blank=True, default='Creative Group', max_length=1000, null=True),
        ),
    ]
