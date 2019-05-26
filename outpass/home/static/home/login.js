function validateSubmit(){
    var email = document.getElementById('email').value;
    var password = document.getElementById('password').value;
    var reg = /^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/;
    if(email == '' || password == '' || !reg.test(email)){
        document.getElementById('email').style.borderColor = '';
        document.getElementById('email-error').style.display = 'none';
        document.getElementById('password').style.borderColor = '';
        document.getElementById('password-error').style.display = 'none';
    if(email == '' || !reg.test(email)){
        document.getElementById('email').style.borderColor = 'red';
        document.getElementById('email-error').style.display = 'block';
    }
    if(password == ''){
        document.getElementById('password').style.borderColor = 'red';
        document.getElementById('password-error').style.display = 'block';
    }
    return false;
}
    return true;
}