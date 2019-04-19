
from django import forms
from . import models

class QuestForm(forms.ModelForm):
    class Meta:
        model = models.Quest
        fields = ['quest_name', 'quest_description', 'quest_points_earned']


class QuestionForm(forms.ModelForm):
    """A form for Free Response Questions to be made"""
    class Meta:
        model = models.Question
        fields = ['question_text']


class IncorrectAnswerForm(forms.ModelForm):
    """A form for wrong answers"""
    class Meta:
        model = models.IncorrectAnswer
        fields = ['question', 'incorrect_answer_text']


class UserForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = ['user_ldap', 'user_first_name', 'user_last_name', 'user_email', 'user_manager_ldap', 
                  'user_director_ldap', 'user_points', 'exempt']


class CorrectAnswerForm(forms.ModelForm):
    class Meta:
        model = models.CorrectAnswer
        fields = ['answer_text']


class WrongAnswerForm(forms.Form):
    incorrect_answer_text = forms.CharField(widget=forms.Textarea)


class TakeInFreeResponseForm(forms.Form):
    answer = forms.CharField()
