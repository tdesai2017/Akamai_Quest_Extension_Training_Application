# Generated by Django 2.0.13 on 2019-06-19 15:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quest_extension', '0038_auto_20190619_1508'),
    ]

    operations = [
        migrations.RenameField(
            model_name='completedquest',
            old_name='user_project',
            new_name='userproject',
        ),
    ]
