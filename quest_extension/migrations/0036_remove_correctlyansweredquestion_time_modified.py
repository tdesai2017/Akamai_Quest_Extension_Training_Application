# Generated by Django 2.0.13 on 2019-06-19 13:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quest_extension', '0035_correctlyansweredquestion_time_modified'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='correctlyansweredquestion',
            name='time_modified',
        ),
    ]