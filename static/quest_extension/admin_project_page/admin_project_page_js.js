bkLib.onDomLoaded(function() {
    nicEditors.editors.push(
        new nicEditor().panelInstance(
            document.getElementById('area1')
        )
    );
});
function show(){
document.getElementById("container").style.display = "inline";
document.getElementById("create_new_project").style.display = "none";
} 
function hide(){
document.getElementById("container").style.display = "none";
document.getElementById("create_new_project").style.display = "inline";
}

function new_pin_and_random_phrase(taken_pins, taken_random_phrases) {
console.log ('I am here')
document.getElementById("invalid_admin_pin").style.display = 'none';
document.getElementById("invalid_random_phrase").style.display = 'none';
pin_input = document.getElementById("id_project_admin_pin").value;
random_phrase_input = document.getElementById("id_project_random_phrase").value;
var all_admin_pins = JSON.parse(taken_pins);
var all_random_phrases =  JSON.parse(taken_random_phrases);
console.log (all_admin_pins.includes(pin_input));
console.log (all_random_phrases.includes(random_phrase_input));
if (all_admin_pins.includes(pin_input) || all_random_phrases.includes(random_phrase_input)) {
    if (all_admin_pins.includes(pin_input)){
        document.getElementById("invalid_admin_pin").style.display = 'inline';
    }
    if (all_random_phrases.includes(random_phrase_input)){
        document.getElementById("invalid_random_phrase").style.display = 'inline';
    }
    return false;
}
else {
    return true;
}


}