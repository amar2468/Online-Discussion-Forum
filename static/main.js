function validate_register_form()
{
    var password_user = document.getElementById("user_password_for_register").value;
    var confirm_password_user = document.getElementById("confirm_password_for_register").value;

    if(password_user.length < 10)
    {
        alert("Password must be at least 10 characters. Enter a new password. ");
        return false;
    }

    if(password_user != confirm_password_user)
    {
        alert("The password and the confirmation of the password do not match!");
        return false;
    }
}

function validate_reset_password_form()
{
    var password_reset = document.getElementById("password_reset").value;
    var confirm_password_reset = document.getElementById("confirm_password_reset").value;

    if(password_reset.length < 10)
    {
        alert("Password must be at least 10 characters. Enter a new password. ");
        return false;
    }

    if(password_reset != confirm_password_reset)
    {
        alert("The password and the confirmation of the password do not match!");
        return false;
    }
}