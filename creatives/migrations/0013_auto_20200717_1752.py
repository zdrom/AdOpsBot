# Generated by Django 3.0.7 on 2020-07-17 17:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('creative_groups', '0006_creativegroup_zip'),
        ('creatives', '0012_auto_20200717_1751'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creative',
            name='creative_group_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='creative_groups.CreativeGroup'),
        ),
    ]
