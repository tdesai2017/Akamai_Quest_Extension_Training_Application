# Generated by Django 2.1.7 on 2019-05-15 17:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CompletedQuest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points_earned', models.IntegerField()),
                ('date_completed', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='CorrectAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer_text', models.CharField(max_length=1000)),
                ('deleted', models.BooleanField(default=False)),
                ('time_modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='CorrectlyAnsweredQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='IncorrectAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer_text', models.CharField(max_length=1000)),
                ('deleted', models.BooleanField(default=False)),
                ('time_modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_name', models.CharField(max_length=1000)),
                ('project_description', models.CharField(max_length=1000)),
                ('project_random_phrase', models.CharField(max_length=255)),
                ('project_editable', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Quest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quest_name', models.CharField(max_length=250)),
                ('quest_description', models.CharField(blank=True, max_length=1000, null=True)),
                ('quest_points_earned', models.IntegerField()),
                ('deleted', models.BooleanField(default=False)),
                ('time_modified', models.DateTimeField(auto_now=True)),
                ('quest_path_number', models.IntegerField()),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quest_extension.Project')),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.CharField(blank=True, max_length=1000, null=True)),
                ('question_type', models.CharField(max_length=45)),
                ('deleted', models.BooleanField(default=False)),
                ('time_modified', models.DateTimeField(auto_now=True)),
                ('quest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quest_extension.Quest')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_ldap', models.CharField(max_length=45)),
                ('user_first_name', models.CharField(max_length=45)),
                ('user_last_name', models.CharField(max_length=45)),
                ('user_email', models.CharField(max_length=45)),
                ('user_manager_ldap', models.CharField(max_length=45)),
                ('user_director_ldap', models.CharField(max_length=45)),
                ('user_password', models.CharField(max_length=45)),
                ('friend', models.CharField(max_length=6)),
            ],
        ),
        migrations.CreateModel(
            name='UserProject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points', models.IntegerField(default=0)),
                ('completed_project', models.BooleanField(default=False)),
                ('current_quest', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='quest_extension.Quest')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quest_extension.Project')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quest_extension.User')),
            ],
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('video_url', models.CharField(max_length=1000)),
                ('video_type', models.CharField(choices=[('Youtube', 'Youtube'), ('Personal', 'Personal')], max_length=1000)),
                ('quest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quest_extension.Quest')),
            ],
        ),
        migrations.AddField(
            model_name='incorrectanswer',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quest_extension.Question'),
        ),
        migrations.AddField(
            model_name='correctlyansweredquestion',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quest_extension.Question'),
        ),
        migrations.AddField(
            model_name='correctlyansweredquestion',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quest_extension.User'),
        ),
        migrations.AddField(
            model_name='correctanswer',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quest_extension.Question'),
        ),
        migrations.AddField(
            model_name='completedquest',
            name='quest',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quest_extension.Quest'),
        ),
        migrations.AddField(
            model_name='completedquest',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quest_extension.User'),
        ),
    ]
