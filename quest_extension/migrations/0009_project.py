# Generated by Django 2.1.7 on 2019-04-26 18:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quest_extension', '0008_auto_20190424_1446'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_name', models.CharField(max_length=1000)),
                ('project_description', models.CharField(max_length=1000)),
            ],
        ),
    ]