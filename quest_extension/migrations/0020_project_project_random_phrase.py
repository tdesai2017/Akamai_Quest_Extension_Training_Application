# Generated by Django 2.1.7 on 2019-04-30 17:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quest_extension', '0019_remove_user_user_points'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='project_random_phrase',
            field=models.CharField(default='default_random_phrase', max_length=255),
        ),
    ]