from django.db import models
from django.db import models
from datetime import datetime
#CASCADE means that the row will be deleted too if the ForeignKey gets deleted.


class Project(models.Model):
    project_name = models.CharField(max_length=1000)
    project_description = models.CharField(max_length=1000)
    project_random_phrase = models.CharField(max_length = 255)

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
    time_modified = models.DateTimeField(auto_now=True)

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
   user_manager_ldap = models.CharField(max_length=45)
   user_director_ldap = models.CharField(max_length=45)
   exempt = models.BooleanField(default=False)

   
class CorrectAnswer(models.Model):
   question = models.ForeignKey(Question, on_delete=models.CASCADE)
   answer_text = models.CharField(max_length=1000)
   deleted = models.BooleanField(default=False)
   time_modified = models.DateTimeField(auto_now=True)

  
class CompletedQuest(models.Model):
   user = models.ForeignKey(User, on_delete=models.CASCADE)
   quest = models.ForeignKey(Quest, on_delete=models.CASCADE)
   points_earned = models.IntegerField()
   date_completed = models.DateTimeField()

class CorrectlyAnsweredQuestion (models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class UserProject(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    current_quest = models.ForeignKey(Quest, on_delete=models.CASCADE)
    points = models.IntegerField(default = 0)





