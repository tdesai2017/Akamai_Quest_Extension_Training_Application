function update(info){
    document.getElementById("update_" + info + "_button").style.display = "none";
    document.getElementById("update_" + info + "_form").style.display = "inline"
  } 

function validate_email() {

document.getElementById('email').style.display = 'none'; 

email = document.getElementById("account_email").value
var email_re = /^\S+@\S+$/;

if (email_re.test(String(email).toLowerCase())) {
    return true;
}

else {
    document.getElementById('email').style.display = 'block'
    return false;
}
}

function validate_password() {
document.getElementById('low').style.display = 'none'; 
document.getElementById('up').style.display = 'none'; 
document.getElementById('num').style.display = 'none'; 
document.getElementById('char').style.display = 'none'; 
document.getElementById('same').style.display = 'none'; 
document.getElementById('email').style.display = 'none'; 


password = document.getElementById("password").value
retyped_password = document.getElementById("retyped_password").value
var count = 0;



if (password == retyped_password) { 
    count += 1;
}

else {
    document.getElementById('same').style.display = 'block'; 
}

if (/[a-z]/.test(password)) { 
    count += 1;
}

else {
    document.getElementById('low').style.display = 'block'; 
}

if (/[A-Z]/.test(password)) {
    count += 1;
    } 

else {
    document.getElementById('up').style.display = 'block';
}

if (/\d/.test(password)) {
    count += 1;
}   
else {
    document.getElementById('num').style.display = 'block';
}

if (password.length >= 8) { 
    count += 1
}
else {
    document.getElementById('char').style.display = 'block';
}

return (count == 5)

}

  