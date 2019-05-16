
from django import forms
from . import models



class QuestForm(forms.ModelForm):
    class Meta:
        model = models.Quest
        fields = ['quest_name', 'quest_description', 'quest_points_earned', 'quest_path_number']


#Records the name of a question
class QuestionForm(forms.ModelForm):
    """A form for Free Response Questions to be made"""
    class Meta:
        model = models.Question
        fields = ['question_text']




class UserForm(forms.ModelForm):
    user_password = forms.CharField(widget=forms.PasswordInput(attrs={'autocomplete' : 'new-password'}))
    class Meta:
        model = models.User
        fields = ['user_ldap', 'user_first_name', 'user_last_name', 'user_email', 
                   'user_password',]
        labels = {'user_ldap': 'LDAP',
                  'user_first_name': 'First Name',
                  'user_last_name': 'Last Name',
                  'user_email': 'Email', 
                  'user_password': 'Password'}


#For free response questions
class CorrectAnswerForm(forms.ModelForm):
    class Meta:
        model = models.CorrectAnswer
        fields = ['answer_text']

class ProjectForm(forms.ModelForm):
    class Meta:
        model = models.Project
        fields = ['project_name', 'project_random_phrase']
        # fields = ['project_name', 'project_description', 'project_random_phrase']
        


#For MC Questions
class RightAnswerForm(forms.Form):
    correct_choices = forms.CharField(widget=forms.Textarea)

class WrongAnswerForm(forms.Form):
    incorrect_choices = forms.CharField(widget=forms.Textarea)

#-------

class TakeInFreeResponseForm(forms.Form):
    answer = forms.CharField()

class AddNewProjectForm(forms.Form):
    random_phrase = forms.CharField()


class LoginForm(forms.Form):
    ldap = forms.CharField(max_length=45, label= 'LDAP')
    password = forms.CharField(widget=forms.PasswordInput(attrs={'autocomplete' : 'new-password'}))



class VideoForm(forms.ModelForm):
    class Meta:
        model = models.Video
        fields = ['video_url', 'video_type']


#-----------------

class ForgotPasswordForm(forms.Form):
    pin = forms.CharField(max_length=100, label='PIN')
    new_password = forms.CharField(label = 'New Password', widget=forms.PasswordInput(attrs={'autocomplete' : 'new-password'}))
    retype_new_password = forms.CharField( label= 'Retype Password', widget=forms.PasswordInput(attrs={'autocomplete' : 'new-password'} ))
        

class AdminForm(forms.ModelForm):
    admin_password = forms.CharField(widget=forms.PasswordInput(attrs={'autocomplete' : 'new-password'}))
    class Meta:
        model = models.Admin
        fields = ['admin_ldap', 'admin_first_name', 'admin_last_name', 'admin_email', 
                   'admin_password',]
        labels = {'admin_ldap': 'LDAP',
                  'admin_first_name': 'First Name',
                  'admin_last_name': 'Last Name',
                  'admin_email': 'Email', 
                  'admin_password': 'Password'}




