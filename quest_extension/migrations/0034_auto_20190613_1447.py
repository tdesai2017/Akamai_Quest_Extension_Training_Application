# Generated by Django 2.0.13 on 2019-06-13 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quest_extension', '0033_quest_quest_picture_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quest',
            name='quest_picture_url',
            field=models.CharField(blank=True, default='', max_length=1000),
        ),
    ]