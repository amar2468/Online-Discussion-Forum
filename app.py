import os
from datetime import date
from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
import db

app = Flask(__name__)
app.secret_key = '32892938832jfdjjkd2993nd'
app.config["SESSION_TYPE"] = "filesystem"

# Route for homepage which also checks whether the user is logged in or not

@app.route('/')
def home():
	collection_info = db.forum_database.ForumPostCollection.find()

	return render_template("home.html", collection_info=collection_info)

# Route for register account which allows the user to register

@app.route('/register_account', methods =["GET", "POST"])
def register_account():
	if not session.get("name"):
		if request.method == "POST":
			fname = request.form.get("first_name")
			lname = request.form.get("last_name")
			email = request.form.get("email_address_for_register")
			passwd = request.form.get("user_password_for_register")
			profile_pic = request.files['profile_picture_for_register']

			if db.register_login_database.RegLoginCollection.find_one({"email": {"$eq": email}}):
				return redirect("/register_account")
			else:
				encrypted_password = generate_password_hash(passwd)

				saving_profile_picture = secure_filename(profile_pic.filename)
				profile_pic.save(os.path.join("static/", saving_profile_picture))

				date_registered = date.today()

				date_registered = date_registered.strftime("%d/%m/%Y")

				db.register_login_database.RegLoginCollection.insert_one({"first_name": fname, "last_name":lname, "email":email, "password": encrypted_password, "profile_picture_link": saving_profile_picture,'user_registered': date_registered})
				
				session["name"] = request.form.get("email_address_for_register")

				session.permanent = True
				
				return redirect("/student_profile")
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

			for document in db.register_login_database.RegLoginCollection.find():
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
	for document in db.register_login_database.RegLoginCollection.find():
		if document["email"] == session["name"]:
			return render_template("student_profile.html", document = document)

# Route created for changing profile picture

@app.route('/changing_profile_picture', methods =["GET", "POST"])
def changing_profile_picture():

	profile_picture = request.files['change_profile_picture_file_upload']
	changing_profile_picture = secure_filename(profile_picture.filename)
	profile_picture.save(os.path.join("static/", changing_profile_picture))
	
	db.register_login_database.RegLoginCollection.update_one(
		{ 'email': session.get("name") },
		{ "$set": { 'profile_picture_link': changing_profile_picture } }
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
		db.register_login_database.RegLoginCollection.update_one(
			{ 'email': session.get("name") },
			{ "$set": { 'password': encrypted_pwd } }
		)
	return redirect("/student_profile")

# Route for forum post render

@app.route('/render_forum_post')
def render_forum_post():
	if session.get("name"):
		return render_template("forum_post.html")
	elif not session.get("name"):
		collection_info = db.forum_database.ForumPostCollection.find()
		return render_template("home.html", collection_info=collection_info)

# Route for viewing topic

@app.route('/view_topic/<_id>')
def view_topic(_id):
	user_info = db.register_login_database.RegLoginCollection.find()

	for document in db.forum_database.ForumPostCollection.find():
		if str(document["_id"]) == _id:
			content_post = document['content_of_post']
			collection_info = db.forum_database.ForumPostCollection.find()

			for user in user_info:
				if user['email'] == document['author_of_post']:
					registration_date_user = user['user_registered']
					break
			return render_template("view_forum_post.html", registration_date_user=registration_date_user, user_info=user_info,content_post = content_post, collection_info=collection_info)
	collection_info = db.forum_database.ForumPostCollection.find()
	return render_template("view_forum_post.html", user_info=user_info, content_post = content_post, collection_info=collection_info)


# Route for rendering template that allows the user to re-enter the information that they want to update

@app.route('/edit_topic/<id_edit>')
def edit_topic(id_edit):
	for document in db.forum_database.ForumPostCollection.find():
		if str(document["_id"]) == id_edit:
			return render_template("update_post.html", document=document ,id_edit=id_edit)

# Route for edit topic
@app.route('/edit_forum_topic/<id_edit>', methods =["GET", "POST"])
def edit_forum_topic(id_edit):

	topic_title = request.form.get("title_of_post")
	topic_content = request.form.get("post_content")

	db.forum_database.ForumPostCollection.update_one(
		{ '_id':  ObjectId(id_edit) },
		{ "$set": { 'title_of_post': topic_title } }
	)

	db.forum_database.ForumPostCollection.update_one(
		{ '_id':  ObjectId(id_edit) },
		{ "$set": { 'content_of_post': topic_content } }
	)

	return redirect("/")

# Route for deleting a topic

@app.route('/delete_topic/<id_delete>')
def delete_topic(id_delete):
	db.forum_database.ForumPostCollection.delete_one( {"_id": ObjectId(id_delete)})

	return redirect("/")

# Route for like post functionality

@app.route('/like_post/<like_post_id>')
def like_post(like_post_id):

	for document in db.forum_database.ForumPostCollection.find():
		if str(document["_id"]) == like_post_id:
			if session.get("name") == document["author_of_post"]:

				if document["user_liked_own_post"] == False:

					db.forum_database.ForumPostCollection.update_one(
						{ '_id':  ObjectId(like_post_id) },
						{ "$set": { 'user_liked_own_post':  True} }
					)

					db.forum_database.ForumPostCollection.update_one(
						{ '_id':  ObjectId(like_post_id) },
						{ "$inc": { 'number_of_likes':  1} }
					)

					db.forum_database.ForumPostCollection.update_one(
						{ '_id':  ObjectId(like_post_id) },
						{ "$push": { 'all_users_who_liked_post': session.get("name") } }
					)
			
			else:
				if session.get("name") not in document["all_users_who_liked_post"] and session.get("name") != None:
					db.forum_database.ForumPostCollection.update_one(
						{ '_id':  ObjectId(like_post_id) },
						{ "$inc": { 'number_of_likes':  1} }
					)

					db.forum_database.ForumPostCollection.update_one(
						{ '_id':  ObjectId(like_post_id) },
						{ "$push": { 'all_users_who_liked_post': session.get("name") } }
					)


	return redirect("/")

# Route for dislike post functionality

@app.route('/dislike_post/<dislike_post_id>')
def dislike_post(dislike_post_id):

	for document in db.forum_database.ForumPostCollection.find():
		if str(document["_id"]) == dislike_post_id:

			if session.get("name") == document["author_of_post"]:

				if document["user_disliked_own_post"] == False:

					db.forum_database.ForumPostCollection.update_one(
						{ '_id':  ObjectId(dislike_post_id) },
						{ "$set": { 'user_disliked_own_post':  True} }
					)

					db.forum_database.ForumPostCollection.update_one(
						{ '_id':  ObjectId(dislike_post_id) },
						{ "$inc": { 'number_of_dislikes':  1} }
					)

					db.forum_database.ForumPostCollection.update_one(
						{ '_id':  ObjectId(dislike_post_id) },
						{ "$push": { 'all_users_who_disliked_post': session.get("name") } }
					)
			
			else:
				if session.get("name") not in document["all_users_who_disliked_post"] and session.get("name") != None:
					db.forum_database.ForumPostCollection.update_one(
						{ '_id':  ObjectId(dislike_post_id) },
						{ "$inc": { 'number_of_dislikes':  1} }
					)

					db.forum_database.ForumPostCollection.update_one(
						{ '_id':  ObjectId(dislike_post_id) },
						{ "$push": { 'all_users_who_disliked_post': session.get("name") } }
					)


	return redirect("/")

# Route for dealing with forum post form

@app.route('/forum_post', methods =["GET", "POST"])
def forum_post():
	if session.get("name"):
		title = request.form.get("title_of_post")
		content = request.form.get("post_content")

		db.forum_database.ForumPostCollection.insert_one({"author_of_post":session.get("name"), "title_of_post": title, "content_of_post": content, "number_of_likes": 0, "number_of_dislikes": 0, "user_liked_own_post": False, "user_disliked_own_post": False, "all_users_who_liked_post": [], "all_users_who_disliked_post": [] })

		return redirect('/')
	elif not session.get("name"):
		return redirect('/')

if __name__ == '__main__':
	app.run(debug=True)
