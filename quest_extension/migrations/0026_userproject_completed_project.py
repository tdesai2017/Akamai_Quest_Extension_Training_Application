# Generated by Django 2.1.7 on 2019-05-03 18:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quest_extension', '0025_auto_20190503_1328'),
    ]

    operations = [
        migrations.AddField(
            model_name='userproject',
            name='completed_project',
            field=models.BooleanField(default=False),
        ),
    ]