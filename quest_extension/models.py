
from django.db import models
from datetime import datetime
from django.db import models

#CASCADE means that the row will be deleted too if the ForeignKey gets deleted.

# Admins are the accounts that can create projects for users to join
class Admin(models.Model):
    admin_ldap = models.CharField(max_length=45)
    admin_first_name = models.CharField(max_length=45)
    admin_last_name = models.CharField(max_length=45)
    admin_email = models.CharField(max_length=45)
    admin_password = models.CharField(max_length = 100)
    admin_reset_password_pin = models.CharField(max_length = 100, null=True)

    # admin_ldap = the admin's ldap -> used for authentication and keeping sessions throughout one's usage of the project to ensure integrity
    # admin_first_name = admin's first name
    # admin_last_name = admin's last name
    # admin_email = admin's email
    # admin_password = admin's password
    # admin_reset_password_pin = this is the pin that will be sent to the admin's email if they want to reset their password.
                                #The admin will have to input this pin in order to successfully change their password. The
                                #pin is reset back to None as soon as validation occurs or as soon as the admin 'goes back'
                                #and exits the reset password page in order to maintain integrity and minimize the gap for insecurity
                                

    

# Projects are the trainings that admins create for users
class Project(models.Model):
    project_name = models.CharField(max_length=1000)
    project_description = models.CharField(max_length=1000, blank = True, null = True)
    project_random_phrase = models.CharField(max_length = 255, unique = True)
    project_admin_pin = models.CharField(max_length = 255, unique = True)
    project_editable = models.BooleanField()
    project_has_teams = models.BooleanField(default = False)

    # project_name = name of the project
    # project_description = description of the project
    # project_random_phrase = this phrase is what users will have to type in order to join a project - it serves so that only the users you want taking the
                                #training will be able to access the project
    # project_admin_pin = this pin is used so that other admins may join your project if you tell them what your pin is
    # project_editable = signifies whether a project is still editable or has become view only
    # project_has_teams = simply specifies whether a certain project contains teams


# A project contains Quests. Quests in turn have questions inside of them. A User must complete all the questions inside of a quest to complete the quest. He or she
# will then move on to the next quest until the user has completed all the quests in a similar fashion. Once they are all complete, the user would have successfully
# completed the project
class Quest(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    quest_name = models.CharField(max_length=250)
    quest_description = models.CharField(max_length=1000, blank=True, null=True)
    quest_points_earned = models.IntegerField()
    time_modified = models.DateTimeField(auto_now=True) #the auto now field gets updated to the current time whenever the quest itself undergoes any change in state
    quest_path_number = models.IntegerField()
    quest_picture_url = models.CharField(max_length = 100000, blank=True, default = '')

    # project = represents the project that the quest is associated with
    # quest_name = name of quest
    # quest_description = description of quest
    # quest_points_earned = points earned by completeing quest
    # time_modified = represents whenever the quest is created or whenever anything about it is changed
    # quest_path_number = represents the path number of the quest/order the users will have to answer it in reference to other quests in the project
    # quest_picture_url = the url of the picture that is being used to represent the quest

# A quest is made up of many questions
class Question(models.Model):
    QUESTION_TYPES = (('MC', 'MC'), ('FR', 'FR'), ('API', 'API'))
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=1000, blank=True, null=True)
    question_type = models.CharField(max_length=45, choices = QUESTION_TYPES)
    deleted = models.BooleanField(default=False)
    # *we undo deletes based on delete_time, and the placement of the reappearing question is based on time_modified
    time_modified = models.DateTimeField(auto_now=True)
    delete_time = models.DateTimeField(auto_now = True)
    #specific to api type questions
    question_api_url = models.CharField(max_length=1000, null=True, default = None)

    # QUESTION_TYPES = (('MC', 'MC'), ('FR', 'FR'), ('API', 'API')) = represents the types that a question can be
    # quest = represents the quest that a question is asscoated with
    # question_text = the text of the question. Ex: 'What is your favorite color?' would be the question_text
    # question_type = type of question from above choices
    # deleted = represents whether the question is 'deleted' or not. I use this instead of fully deleting it since now we can undo a delete as well
    # time_modified = Represents when a question is modified or created
    # delete_time = Represents the time a question was deleted 
    # question_api_url = represents the url for an api question -> this is set to None in all questions that are not API based


# This class is only used with multiple choice questions, since an mc question will have both correct and incorrect answers that will be set by the admin
class IncorrectAnswer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.CharField(max_length=10000)
    time_modified = models.DateTimeField(auto_now=True)

    # question = represents the question that an incorrect answer is associated with
    # answer_text = the text associated with an incorrect answer
    # time_modified = time that the incorrect answer was created or modified
 

# Users join and partake in training projects that were created by admins
class User(models.Model):
    user_ldap = models.CharField(max_length=45)
    user_first_name = models.CharField(max_length=45)
    user_last_name = models.CharField(max_length=45)
    user_email = models.CharField(max_length=45)
    user_password = models.CharField(max_length = 100)
    user_reset_password_pin = models.CharField(max_length = 100, null=True, default = None)

    # user_ldap = the user's ldap -> used for authentication and keeping sessions throughout one's usage of the project to ensure integrity
    # user_first_name = user's first name
    # user_last_name = user's last name
    # user_email = user's email
    # user_password = user's password
    # user_reset_password_pin = this is the pin that will be sent to the user's email if they want to reset their password.
                                #The user will have to input this pin in order to successfully change their password. The
                                #pin is reset back to None as soon as validation occurs or as soon as the user 'goes back'
                                #and exits the reset password page in order to maintain integrity and minimize the gap for insecurity
   
   
# Represents the correct answer to a questions
class CorrectAnswer(models.Model):
   question = models.ForeignKey(Question, on_delete=models.CASCADE)
   answer_text = models.CharField(max_length=10000)
   time_modified = models.DateTimeField(auto_now=True)

   # question = represents the question that a correct answer is associated with
    # answer_text = the text associated with a correct answer
    # time_modified = time that the correct answer was created or modified


# A project can optionally have teams which users will join to partake in the project 
class Team(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    team_name = models.CharField(max_length= 100)

    # project = represents project that a team is associated with
    # team_name = represents textual name of the team

# This is the class that joins a user to a project -> since projects can have many users and users can be a part of many projects, this
# allows us to differentiate between different instances of user-project pairs. For example. The points that a user has in one project will
# not be equal to the amount of points he has in another project. Thus, all of this information that is distinct to a user's experience with
# a specific project is encapsulated in this class
class UserProject(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    current_quest = models.ForeignKey(Quest, on_delete=models.CASCADE, null=True)
    points = models.IntegerField(default = 0)
    completed_project = models.BooleanField(default=False)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null = True)
    archived = models.BooleanField(default = False)

    # user = user that the userproject is associated with
    # project = project that the userproject is associated with
    # current_quest = current quest that the user in on in this specific project
    # points = points that the user has in this project
    # completed_project = signifies whether the user has compelted the current_project
    # team = signifies the team that the user is on for this project
    # archived = signifies whether this project is archived or not


# Represents whether a user-project's user has successfully completed a quest
class CompletedQuest(models.Model):
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE)
    userproject = models.ForeignKey(UserProject, on_delete=models.CASCADE)
    time_completed = models.DateTimeField(null = True)

    # quest = represents the quest that has been completed
    # userproject = represents the userproject that has completed this quest
    # time_completed = represents the time that this quest was completed -> used to generated the 'recently awarded points' display since a user gets points
                        #every time he or she completes a quest


# Represent's whether a user-project's user has correctly answered a question
# When a record for this class appears (one a user correctly answers a question), that question no longer becomes available for them to answer
class CorrectlyAnsweredQuestion(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    userproject = models.ForeignKey(UserProject, on_delete=models.CASCADE, null=True)

    # question = represents the question that has been correctly answered by the user
    # userproejct = represents the userproejct that has successfully answered this question
    
# Represents a video that an admin may want to embed into a quest
class Video(models.Model):
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE)
    video_url = models.CharField(max_length = 1000)

    # quest = quest that a video is associated with
    # video_url = url for the video that is to be displayed


#This is the class that joins admins to projects -> it is the same concept as the userproject class. An admin-project relationship is determined by whether
#it is present in this model
class AdminProject(models.Model):
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    archived = models.BooleanField(default = False)

    # admin = the admin that the admin project is associated to
    # project = the project that the admin has joined/now has admin access over
    # archived = whether the admin has archived this project for him/herself


    







    
