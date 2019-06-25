
from django import forms
from . import models



class QuestForm(forms.ModelForm):
    class Meta:
        model = models.Quest
        fields = ['quest_name', 'quest_points_earned', 'quest_path_number', 'quest_picture_url']


#Records the name of a question
class QuestionForm(forms.ModelForm):
    """A form for Free Response Questions to be made"""
    class Meta:
        model = models.Question
        fields = ['question_text']




class UserForm(forms.ModelForm):
    user_ldap = forms.CharField(label = '', widget=forms.TextInput(attrs={'placeholder':'LDAP'}))
    user_first_name = forms.CharField(label = '', widget=forms.TextInput(attrs={ 'placeholder':'First Name'}))
    user_last_name = forms.CharField(label = '',widget=forms.TextInput(attrs={ 'placeholder':'Last Name'}))
    user_email = forms.CharField(label = '', widget=forms.TextInput(attrs={ 'placeholder':'Email'}))
    user_password = forms.CharField(label = '', widget=forms.PasswordInput(attrs={'placeholder':'Password'}))
    class Meta:
        model = models.User
        fields = ['user_ldap', 'user_first_name', 'user_last_name', 'user_email', 
                   'user_password',]
        


#For free response questions
class CorrectAnswerForm(forms.ModelForm):
    class Meta:
        model = models.CorrectAnswer
        fields = ['answer_text']

class ProjectForm(forms.ModelForm):
    class Meta:
        model = models.Project
        fields = ['project_name', 'project_random_phrase', 'project_admin_pin']
        # fields = ['project_name', 'project_description', 'project_random_phrase']
        


#For MC Questions
class RightAnswerForm(forms.Form):
    correct_choices = forms.CharField(widget=forms.Textarea)

class WrongAnswerForm(forms.Form):
    incorrect_choices = forms.CharField(widget=forms.Textarea)

#-------

class TakeInFreeResponseForm(forms.Form):
    answer = forms.CharField()


class LoginForm(forms.Form):
    ldap = forms.CharField(max_length=45, label= '', widget=forms.TextInput(attrs={'placeholder': 'LDAP'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'autocomplete' : 'new-password', 'placeholder': 'Password'}), label = '')



class VideoForm(forms.ModelForm):
    class Meta:
        model = models.Video
        fields = ['video_url']


#-----------------

class ForgotPasswordForm(forms.Form):
    pin = forms.CharField(max_length=100, label='PIN')
    new_password = forms.CharField(label = 'New Password', widget=forms.PasswordInput(attrs={'autocomplete' : 'new-password'}))
    retype_new_password = forms.CharField( label= 'Retype Password', widget=forms.PasswordInput(attrs={'autocomplete' : 'new-password'} ))
        

class AdminForm(forms.ModelForm):
    admin_ldap = forms.CharField(label = '', widget=forms.TextInput(attrs={'placeholder' : 'LDAP'}))
    admin_first_name = forms.CharField(label = '', widget=forms.TextInput(attrs={'placeholder' : 'First Name'}))
    admin_last_name = forms.CharField(label = '', widget=forms.TextInput(attrs={'placeholder' : 'Last Name'}))
    admin_email = forms.CharField(label = '', widget=forms.TextInput(attrs={'placeholder' : 'Email'}))
    admin_password = forms.CharField(label = '', widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'autocomplete' : 'new-password'}))
    class Meta:
        model = models.Admin
        fields = ['admin_ldap', 'admin_first_name', 'admin_last_name', 'admin_email', 
                   'admin_password',]
       


