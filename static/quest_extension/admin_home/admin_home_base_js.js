function show(){
    document.getElementById("edit_description_container").style.display = "inline";
    document.getElementById("edit_description_button").style.display = "none";
    document.getElementById("my-text-area").style.display = "none";
  } 
    function show_update_name(){
        document.getElementById("edit_name_container").style.display = "inline";
        document.getElementById('edit_name_button').style.display = 'none';
    }

    function show_update_picture(quest_id){
        document.getElementById("edit_picture_container_" + quest_id).style.display = "inline";
        document.getElementById('edit_picture_button_' + quest_id).style.display = 'none';
    }

    function show_plain_button_instead(quest_id){

        document.getElementById('image_submit_' + quest_id).style.display = 'none'
        document.getElementById('button_submit_'+ quest_id).style.display = 'inline'
    }