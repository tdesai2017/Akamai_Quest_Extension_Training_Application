# Generated by Django 2.1.7 on 2019-05-03 13:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quest_extension', '0024_user_user_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='user_password',
            field=models.CharField(max_length=45),
        ),
    ]