function validate_fr_answer(question_id, q_to_a){

    var user_answer = document.getElementById('input_'+ question_id).value.trim();
    var q_to_a_json = JSON.parse(q_to_a);
    var answer_to_this_question = q_to_a_json[question_id]
        if (user_answer == answer_to_this_question) {
            document.getElementById('correct_' + question_id).style.display = 'inline'
            document.getElementById('wrong_' + question_id).style.display = 'none'

        }
        else {
            document.getElementById('wrong_' + question_id).style.display = 'inline'
            document.getElementById('correct_' + question_id).style.display = 'none'

        }

    return false;
}

function validate_mc_answer(question_id, q_to_a){
    var q_to_a_json = JSON.parse(q_to_a);
    var answer_to_this_question = q_to_a_json[question_id]
    
    
    var user_input= document.querySelectorAll('.input_' + question_id)
    checked_list = []
    for (var i=0;i<user_input.length;i++){
        if (user_input[i].checked) {
            checked_list.push(user_input[i].value.trim())
        }
    }  
    

    user_answer = checked_list.sort().toString()
    answer_to_this_question = answer_to_this_question.sort().toString()

    if (user_answer == answer_to_this_question) {
            document.getElementById('correct_' + question_id).style.display = 'inline'
            document.getElementById('wrong_' + question_id).style.display = 'none'

        }
        else {
            document.getElementById('wrong_' + question_id).style.display = 'inline'
            document.getElementById('correct_' + question_id).style.display = 'none'

        }

    return false;
}


