function validate_form()
{
    var password_user = document.getElementById("user_password_for_register").value;
    var confirm_password_user = document.getElementById("confirm_password_for_register").value;

    if(password_user.length < 10)
    {
        alert("Password must be at least 10 characters. Enter a new password. ");
    }

    if(password_user != confirm_password_user)
    {
        alert("The password and the confirmation of the password do not match!");
    }
}