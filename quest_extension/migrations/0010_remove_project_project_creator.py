# Generated by Django 2.1.7 on 2019-05-17 14:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quest_extension', '0009_project_project_creator'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='project_creator',
        ),
    ]
