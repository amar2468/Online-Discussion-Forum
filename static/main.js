function validate_register_form()
{
    var password_user = document.getElementById("user_password_for_register").value;
    var confirm_password_user = document.getElementById("confirm_password_for_register").value;
    var check_age_for_register = document.getElementById("check_age_for_register");
    let check_password_requirement = new RegExp('(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[^A-Za-z0-9])(?=.{10,})')


    if (check_age_for_register.checked == false)
    {
        alert("You must be at least 16, in order to register an account: ");
        return false;
    }
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

    if(check_password_requirement.test(password_user))
    {
        return;
    }
    else
    {
        alert("Password must contain at least one uppercase character, one lowercase character, one number and a special character. ");
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

/*
function get_file_path_profile_picture()
{
    let file_path = document.getElementById("change_profile_picture_file_upload").value;

}
*/