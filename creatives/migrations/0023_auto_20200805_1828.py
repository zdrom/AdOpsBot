# Generated by Django 3.0.7 on 2020-08-05 18:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('creatives', '0022_auto_20200803_1718'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creative',
            name='name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
