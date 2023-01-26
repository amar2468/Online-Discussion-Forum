function validate_register_form()
{
    // Declaring variables that will be used to validate the register form

    let first_name = document.getElementById("first_name").value;
    let last_name = document.getElementById("last_name").value;
    let email = document.getElementById("email_address_for_register").value;
    let password_user = document.getElementById("user_password_for_register").value;
    let confirm_password_user = document.getElementById("confirm_password_for_register").value;
    let check_age_for_register = document.getElementById("check_age_for_register");
    let check_password_requirement = new RegExp('(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[^A-Za-z0-9])(?=.{10,})')

    // Referencing all the error paragraphs
    let all_errors = document.querySelectorAll(".error");

    // Iterate through each error
	for(let error of all_errors)
    {
        // Hide the error message
		error.style.display = "none";
	}

    // If the user does not enter the first name
    if (first_name == "")
    {
        // Show the relevant error message as a block
        document.querySelector(".name-error").innerHTML = "Please enter a name";
        document.querySelector(".name-error").style.display = "block";
        return false;
    }

    // If the user does not enter the last name
    if (last_name == "")
    {
        // Show the relevant error message as a block
        document.querySelector(".lastname-error").innerHTML = "Please enter a surname";
        document.querySelector(".lastname-error").style.display = "block";
        return false;
    }

    // If the user does not enter the email
    if (email == "")
    {
        // Show the relevant error message as a block
        document.querySelector(".email-error").innerHTML = "Please enter an email";
        document.querySelector(".email-error").style.display = "block";
        return false;
    }

    // If the password entered is less than 10 characters
    if(password_user.length < 10)
    {
        // Show the relevant error message as a block
        document.querySelector(".password-error").innerHTML = "Password must be at least 10 characters. Enter a new password";
        document.querySelector(".password-error").style.display = "block";
        return false;
    }

    // If the password is not as required
    if(!check_password_requirement.test(password_user))
    {
        if (password_user != "")
        {
            // Error message telling the user what needs to be contained within a password
            document.querySelector(".password-error").innerHTML = "Password must contain at least one uppercase character, one lowercase character, one number and a special character";
            document.querySelector(".password-error").style.display = "block";
            return false;
        }
    }

    // If the user does not confirm the password
    if (confirm_password_user == "")
    {
        // Show the relevant error message as a block
        document.querySelector(".confirmpass-error").innerHTML = "Please confirm your password";
        document.querySelector(".confirmpass-error").style.display = "block";
        return false;
    }

    // If the password entered does not match the field where the user confirms their password
    if(password_user != confirm_password_user)
    {
        // Show the relevant error message as a block
        document.querySelector(".confirmpass-error").innerHTML = "The password and the confirmation of the password do not match";
        document.querySelector(".confirmpass-error").style.display = "block";
        return false;
    }

    // If the checkbox is not checked
    if (check_age_for_register.checked == false)
    {
        // Show the relevant error message as a block
        document.querySelector(".checkbox-error").innerHTML = "Please confirm whether you are over 16 years of age";
        document.querySelector(".checkbox-error").style.display = "block";
        return false;
    }
}

function validate_reset_password_form()
{
    // Declaring the password variables that have been referenced from the html page
    let password_reset = document.getElementById("password_reset").value;
    let confirm_password_reset = document.getElementById("confirm_password_reset").value;
    let check_password_requirement = new RegExp('(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[^A-Za-z0-9])(?=.{10,})')

    // Referencing all the error paragraphs
    let all_errors = document.querySelectorAll(".error");

    // Iterate through each error
    for(let error of all_errors)
    {
        // Hide the error message
        error.style.display = "none";
    }

    // If the password length is less than 10
    if(password_reset.length < 10)
    {
        // Error message telling the user to enter at least 10 characters for the password
        document.querySelector(".password-error").innerHTML = "Password must be at least 10 characters. Enter a new password";
        document.querySelector(".password-error").style.display = "block";
        return false;
    }

    // If the password is not as required
    if(!check_password_requirement.test(password_reset))
    {
        if (password_reset != "")
        {
            // Error message telling the user what needs to be contained within a password
            document.querySelector(".password-error").innerHTML = "Password must contain at least one uppercase character, one lowercase character, one number and a special character";
            document.querySelector(".password-error").style.display = "block";
            return false;
        }
    }

    // If the password is not equal to the one that was entered in the confirm password field
    if(password_reset != confirm_password_reset)
    {
        // Error message telling the user that the passwords do not match
        document.querySelector(".confirmpass-error").innerHTML = "The password and the confirmation of the password do not match";
        document.querySelector(".confirmpass-error").style.display = "block";
        return false;
    }
}

function validate_profile_picture()
{
    let check_profile_picture = document.getElementById("change_profile_picture_file_upload").value;

    if (check_profile_picture == "")
    {
        document.querySelector(".profilepicture-error").innerHTML = "You have not selected a profile picture";
        document.querySelector(".profilepicture-error").style.display = "block";
        return false;
    }
}

function delete_topic()
{
    const response_to_delete_prompt = confirm("Are you sure you want to delete the topic?");

    if (response_to_delete_prompt) 
    {
        return;
    }

    else
    {
        return false;
    }
}

function validate_login_form()
{
    login_email = document.getElementById("email_address_for_login").value;
    login_password = document.getElementById("user_password_for_login").value;

    // Referencing all the error paragraphs
    let all_errors = document.querySelectorAll(".error");

    // Iterate through each error
    for(let error of all_errors)
    {
        // Hide the error message
        error.style.display = "none";
    }

    // If the user does not enter the email
    if (login_email == "")
    {
        // Show the relevant error message as a block
        document.querySelector(".email-error").innerHTML = "Please enter an email";
        document.querySelector(".email-error").style.display = "block";
        return false;
    }

    if (login_password == "")
    {
        // Show the relevant error message as a block
        document.querySelector(".password-error").innerHTML = "Please enter a password";
        document.querySelector(".password-error").style.display = "block";
        return false;
    }
}

function reply_to_post()
{
    let reply_content = document.getElementById("reply_content").value;

    if(reply_content == "")
    {
        alert("No comment has been made. Not submitted");
        return false;
    }
}