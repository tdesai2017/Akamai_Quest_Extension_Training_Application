
from django import forms
from . import models

class QuestForm(forms.ModelForm):
    class Meta:
        model = models.Quest
        fields = ['quest_name', 'quest_description', 'quest_points_earned', 'quest_path_number']


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

# FAVORITE_COLORS_CHOICES = (
#     ('blue', 'Blue'),
#     ('green', 'Green'),
#     ('black', 'Black'),
# )

# class TakeInMultipleChoiceForm(forms.Form):
#     answer = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=(FAVORITE_COLORS_CHOICES))

# Straight from https://docs.djangoproject.com/en/2.2/ref/forms/widgets/
# BIRTH_YEAR_CHOICES = ('1980', '1981', '1982')
# FAVORITE_COLORS_CHOICES = (
#     ('blue', 'Blue'),
#     ('green', 'Green'),
#     ('black', 'Black'),
# )

# class TakeInMultipleChoiceForm(forms.Form):
#     birth_year = forms.DateField(widget=forms.SelectDateWidget(years=BIRTH_YEAR_CHOICES))
#     favorite_colors = forms.MultipleChoiceField(
#         required=False,
#         widget=forms.CheckboxSelectMultiple,
#         choices=FAVORITE_COLORS_CHOICES,
#     )


