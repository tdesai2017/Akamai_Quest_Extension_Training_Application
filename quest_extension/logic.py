from django.shortcuts import render
from django.http import HttpResponse
from quest_extension.models import *
from .forms import *
from django.http import HttpResponseRedirect
from django.utils.text import slugify
from django.utils.http import urlencode
from random import shuffle
from django.core.validators import validate_email 
from django.contrib import messages
from datetime import datetime
import copy

#Saves a free response question to the backend
def save_fr_question(question_form, answer_form, quest_id, timestamp=datetime.now()):
    quest = Quest.objects.get(id=quest_id)
    bbb = question_form.save(commit=False)
    bbb.question_type = 'FR'
    
    bbb.quest = quest
    bbb.save()
    question_id = bbb.id
    Question.objects.filter(id = question_id).update(time_modified = timestamp)
    current_question = Question.objects.get(id = question_id)
    print(current_question.time_modified)

    ccc = answer_form.save(commit=False)
    ccc.question = Question.objects.get(id=question_id)
    ccc.save()
    return HttpResponseRedirect('/quest/admin_quest_page_editable/' + str(quest_id))


#Saves a multiple choice question to the backend
def save_mc_question(question_form, answer_form, wrong_answer_form, quest_id, timestamp=datetime.now()):

    quest_id = str(quest_id)
    quest = Quest.objects.get(id=quest_id)
    bbb = question_form.save(commit=False)
    bbb.question_type = 'MC'
    bbb.quest = quest
    bbb.save()
    question_id = bbb.id
    #This allows us to bypass the automatic date from auto_now
    Question.objects.filter(id = question_id).update(time_modified = timestamp)
    
    current_question = Question.objects.get(id = question_id)
    print(current_question.time_modified)
    

    list_of_correct_answers = answer_form.cleaned_data['correct_choices'].split('\n')
    #Removes blank correct answers
    list_of_correct_answers = [x for x in list_of_correct_answers if len(x.strip())>0]


    for correct_answer in list_of_correct_answers:
        correct_answer = str(correct_answer).strip()
        ccc = CorrectAnswer(question=Question.objects.get(id=question_id), answer_text= correct_answer)
        ccc.save()

    list_of_wrong_answers = wrong_answer_form.cleaned_data['incorrect_choices'].split('\n')
    #Removes blank wrong answers
    list_of_wrong_answers = [x for x in list_of_wrong_answers if len(x.strip())>0]


    for wrong_answer in list_of_wrong_answers:
        wrong_answer = str(wrong_answer).strip()
        ddd = IncorrectAnswer(question=Question.objects.get(id=question_id), answer_text= wrong_answer)
        ddd.save()

    return HttpResponseRedirect('/quest/admin_quest_page_editable/' + quest_id)



#Verifies that you are only trying to access the content for the ldap that you are logged in for
def validate_user_access(session_ldap, current_ldap):
    return (session_ldap == current_ldap)
        
    

#Checks whether you can go to the next question once you sumbit a new answer
def go_to_next_quest(current_quest, current_user, current_project):
    num_questions_in_quest = len(Question.objects.filter(quest = current_quest, deleted = False))
    all_questions_in_quest = [question for question in Question.objects.filter(quest = current_quest, deleted = False)]
    count_of_correctly_answered_questions = 0
    for question in all_questions_in_quest:
        if (CorrectlyAnsweredQuestion.objects.filter(question = question, user = current_user)):
            count_of_correctly_answered_questions += 1
            
    print(count_of_correctly_answered_questions, num_questions_in_quest)

    if (count_of_correctly_answered_questions == num_questions_in_quest):
        users_user_project_object = UserProject.objects.get(user = current_user, project = current_project)
        #adds points for the completed quest to the user
        users_user_project_object.points += current_quest.quest_points_earned
        users_user_project_object.save()
        print("Edli's points are:" + str (users_user_project_object.points))
        current_quest_num = current_quest.quest_path_number
        #If next quest exists
        if (Quest.objects.filter(quest_path_number = current_quest_num + 1, project = current_project)):
            next_quest = Quest.objects.get(quest_path_number = current_quest_num + 1, project = current_project)
            print("I Am Here")
            users_user_project_object.current_quest = next_quest
            users_user_project_object.save()
        else:
            users_user_project_object.completed_project = True
            users_user_project_object.save()
            
