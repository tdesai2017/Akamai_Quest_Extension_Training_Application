# Generated by Django 2.1.7 on 2019-06-03 15:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quest_extension', '0027_auto_20190603_1433'),
    ]

    operations = [
        migrations.RenameField(
            model_name='question',
            old_name='api_url',
            new_name='question_api_url',
        ),
    ]
