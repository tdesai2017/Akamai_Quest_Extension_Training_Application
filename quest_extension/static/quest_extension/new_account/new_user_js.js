function validate_password() {
    document.getElementById('low').style.display = 'none'; 
    document.getElementById('up').style.display = 'none'; 
    document.getElementById('num').style.display = 'none'; 
    document.getElementById('char').style.display = 'none'; 
    document.getElementById('same').style.display = 'none'; 
    document.getElementById('email').style.display = 'none'; 


    email = document.getElementById("id_user_email").value
    var email_re = /^\S+@\S+$/;
    
    password = document.getElementById("id_user_password").value
    retyped_password = document.getElementById("retyped_password").value
    var count = 0;

    if (email_re.test(String(email).toLowerCase())) {
        count += 1;
    }

    else {
        document.getElementById('email').style.display = 'block'
    }

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

    return (count == 6)


}