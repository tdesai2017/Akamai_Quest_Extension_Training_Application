
from django.db import models
from datetime import datetime
from django.db import models

#CASCADE means that the row will be deleted too if the ForeignKey gets deleted.

class Admin(models.Model):
    admin_ldap = models.CharField(max_length=45)
    admin_first_name = models.CharField(max_length=45)
    admin_last_name = models.CharField(max_length=45)
    admin_email = models.CharField(max_length=45)
    admin_password = models.CharField(max_length = 100)
    admin_reset_password_pin = models.CharField(max_length = 100, null=True)


class Project(models.Model):
    project_name = models.CharField(max_length=1000)
    project_description = models.CharField(max_length=1000)
    project_random_phrase = models.CharField(max_length = 255, unique = True)
    project_admin_pin = models.CharField(max_length = 255, unique = True)
    project_editable = models.BooleanField()
    project_has_teams = models.BooleanField(default = False)

class Quest(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    quest_name = models.CharField(max_length=250)
    quest_description = models.CharField(max_length=1000, blank=True, null=True)
    quest_points_earned = models.IntegerField()
    deleted = models.BooleanField(default=False)
    time_modified = models.DateTimeField(auto_now=True)
    #Path number determines the order that you want quests to be accessed
    quest_path_number = models.IntegerField()


class Question(models.Model):
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=1000, blank=True, null=True)
    question_type = models.CharField(max_length=45)
    deleted = models.BooleanField(default=False)
    # The advantage of having both time_modified and delete_time -> when we undo a delete,
    # the most recently deleted item will be returned at it's original position (we save the 
    # old timestamp when items are deleted)
    time_modified = models.DateTimeField(auto_now=True)
    delete_time = models.DateTimeField(auto_now = True)

class IncorrectAnswer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.CharField(max_length=1000)
    deleted = models.BooleanField(default=False)
    time_modified = models.DateTimeField(auto_now=True)
 

  
class User(models.Model):
    #Figure out if this on cascade is correct
    user_ldap = models.CharField(max_length=45)
    user_first_name = models.CharField(max_length=45)
    user_last_name = models.CharField(max_length=45)
    user_email = models.CharField(max_length=45)
    user_password = models.CharField(max_length = 100)
    user_reset_password_pin = models.CharField(max_length = 100, null=True, default = None)
   #exempt = models.BooleanField(default=False) (This should go in )
   
   
class CorrectAnswer(models.Model):
   question = models.ForeignKey(Question, on_delete=models.CASCADE)
   answer_text = models.CharField(max_length=1000)
   deleted = models.BooleanField(default=False)
   time_modified = models.DateTimeField(auto_now=True)

  
# class CompletedQuest(models.Model):
#    user = models.ForeignKey(User, on_delete=models.CASCADE)
#    quest = models.ForeignKey(Quest, on_delete=models.CASCADE)
#    points_earned = models.IntegerField()
#    date_completed = models.DateTimeField()



class Team(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    team_name = models.CharField(max_length= 100)

class UserProject(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    #Fix what happens if a single quest gets deleted
    current_quest = models.ForeignKey(Quest, on_delete=models.CASCADE, null=True)
    points = models.IntegerField(default = 0)
    completed_project = models.BooleanField(default=False)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null = True)


class CorrectlyAnsweredQuestion(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    userproject = models.ForeignKey(UserProject, on_delete=models.CASCADE, null=True)

    

class Video(models.Model):
    # VIDEO_TYPES = (
    # ('Youtube', 'Youtube'),
    # ('Personal', 'Personal'))
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE)
    video_url = models.CharField(max_length = 1000)
    # video_type = models.CharField(max_length = 1000, choices = VIDEO_TYPES)



class AdminProject(models.Model):
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)







    
