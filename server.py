from flask import Flask, render_template, request, redirect, session
from flask_session import Session
import db

app = Flask(__name__)
app.secret_key = 'super secret key'
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

			db.db.RegLoginCollection.insert_one({"first_name": fname, "last_name":lname, "email":email, "password": passwd})
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
					if password_for_login == document["password"]:
						session["name"] = request.form.get("email_address_for_login")
						session.permanent = True
						return redirect("/")
				elif email_for_login != document["email"] or password_for_login != document["password"]:
					return 'Incorrect email or password'
		else:
			return render_template("Login.html")
	else:
		return "You are already logged in"

# Route created so that the user can logout when they want to

@app.route('/logout')
def logout():
	if session.get("name"):
		session["name"] = None
		return redirect("/")

if __name__ == '__main__':
	app.run()