from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def test_login():
    # Install the driver so that the automation test can be done
    driver = webdriver.Chrome(ChromeDriverManager().install())

    # Go to the login/sign in page
    driver.get("http://studentdiscussiontest-env.eba-ycpiemz9.us-east-1.elasticbeanstalk.com/login_account")
    
    # Get the email field by id and then fill in the email to test
    email = driver.find_element(By.ID, "email_address_for_login")
    email.send_keys("amar@gmail.com")

    # Get the password field by id and then fill in the password to test
    password = driver.find_element(By.ID, "user_password_for_login")
    password.send_keys("Thispass12!")
    
    # Find the button that contains the text "Sign In" and then click on it
    sign_in = driver.find_element(By.XPATH, "//button[contains(text(), 'Sign In')]")
    sign_in.click()
    
    # Check that the url redirected correctly where it should
    assert driver.current_url.endswith("/student_profile")
    print("The student_profile page was loaded after logging in")
    
    # Find an <a> link that has the keyword "Log Out" and click on it
    logout = driver.find_element(By.XPATH, "//a[contains(text(), 'Log Out')]")
    logout.click()

    # Check that it redirected back to where it should, after logging out
    assert driver.current_url.endswith("/login_account")
    print("After logging out, the login_account page was loaded")

    driver.quit()
test_login()