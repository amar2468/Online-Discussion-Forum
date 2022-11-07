import profile
from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import db

app = Flask(__name__)
app.secret_key = '32892938832jfdjjkd2993nd'
app.config["SESSION_TYPE"] = "filesystem"

# Route for homepage which also checks whether the user is logged in or not

@app.route('/')
def home():
	if session.get("name"):
		return 'Welcome ' + session.get("name")
	elif not session.get("name"):
		return render_template("home.html")

# Route for register account which allows the user to register

@app.route('/register_account', methods =["GET", "POST"])
def register_account():
	if not session.get("name"):
		if request.method == "POST":
			fname = request.form.get("first_name")
			lname = request.form.get("last_name")
			email = request.form.get("email_address_for_register")
			passwd = request.form.get("user_password_for_register")
			check_the_age = request.form.get("check_age_for_register")
			profile_pic = request.form.get("profile_picture_for_register")

			encrypted_password = generate_password_hash(passwd)

			db.db.RegLoginCollection.insert_one({"first_name": fname, "last_name":lname, "email":email, "password": encrypted_password, "profile_picture_link": profile_pic})

			return redirect("/login_account")
		else:
			return render_template("RegisterAccount.html")
	else:
		return 'You are already logged in'

# Route for login account which allows the user to log in

@app.route('/login_account', methods =["GET", "POST"])
def login_account():
	if not session.get("name"):
		if request.method == "POST":
			email_for_login = request.form.get("email_address_for_login")
			password_for_login = request.form.get("user_password_for_login")

			for document in db.db.RegLoginCollection.find():
				if email_for_login == document["email"]:
					if check_password_hash(document["password"],password_for_login):
						session["name"] = request.form.get("email_address_for_login")
						session.permanent = True
						return redirect("/student_profile")
			return redirect("/login_account")
		else:
			return render_template("Login.html")
	else:
		return "You are already logged in"

# Route created so that the user can logout when they want to

@app.route('/logout')
def logout():
	if session.get("name"):
		session["name"] = None
		return redirect("/login_account")
	else:
		return 'Cannot logout when you are not logged in'

# Route created for student profile

@app.route('/student_profile')
def student_profile():
	for document in db.db.RegLoginCollection.find():
		if document["email"] == session["name"]:
			return render_template("student_profile.html", document = document)

# Route created for changing profile picture

@app.route('/changing_profile_picture', methods =["GET", "POST"])
def changing_profile_picture():
	change_profile_pic = request.form.get("change_profile_picture_file_upload")

	db.db.RegLoginCollection.update_one(
		{ 'email': session.get("name") },
		{ "$set": { 'profile_picture_link': change_profile_pic } }
	)

	return redirect("/student_profile")


# Route created to render the forgot password html template

@app.route('/render_forgot_password_template', methods =["GET", "POST"])
def render_forgot_password_template():
	return render_template("forgot_password.html")

# Route created for forgot password

@app.route('/forgot_password', methods =["GET", "POST"])
def forgot_password():
	pwd_reset = request.form.get("password_reset")
	confirm_pwd_reset = request.form.get("confirm_password_reset")

	encrypted_pwd = generate_password_hash(pwd_reset)

	if pwd_reset == confirm_pwd_reset:
		db.db.RegLoginCollection.update_one(
			{ 'email': session.get("name") },
			{ "$set": { 'password': encrypted_pwd } }
		)
	return redirect("/student_profile")

if __name__ == '__main__':
	app.run(debug=True)