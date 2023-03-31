# Project imports needed
from flask_socketio import SocketIO
from flask_recaptcha import ReCaptcha
import os
from datetime import date, datetime
from flask import Flask, flash, render_template, request, redirect, session, jsonify, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
from flask_share import Share
import db
import nltk
import string
from jinja2 import TemplateError
from nltk import pos_tag
from collections import defaultdict
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from collections import defaultdict
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import precision_score, recall_score, f1_score

# Download from nltk library the following:
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')

# Initialize the lemmatizer
lemmatizer = WordNetLemmatizer()

# Below is needed so that words are properly formatted based on wordnet
tag_map = defaultdict(lambda : wordnet.NOUN)
tag_map['J'] = wordnet.ADJ
tag_map['V'] = wordnet.VERB
tag_map['R'] = wordnet.ADV

# Instance of share created to enable sharing
share = Share()

# Getting everything set up
app = Flask(__name__)
app.secret_key = '32892938832jfdjjkd2993nd'
app.config["SESSION_TYPE"] = "filesystem"
app.config['RECAPTCHA_SITE_KEY'] = '6LdLq0AlAAAAAGwZYzeryQrqgn2oXOmhpsUjE1J5'
app.config['RECAPTCHA_SECRET_KEY'] = '6LdLq0AlAAAAAEEcV6ZA-GXSwkE1lRS1W0bLMF_E'
recaptcha = ReCaptcha(app)

share.init_app(app)

socketio = SocketIO(app)

# If page not found, this will execute

@app.errorhandler(404)
def page_not_found(error):
    notifications_info,number_of_notifications = getting_notification_details()
    return render_template('404.html', notifications_info=notifications_info,number_of_notifications=number_of_notifications), 404

# Dealing with error code 400 below

@app.errorhandler(400)
def page_no(error):
    notifications_info,number_of_notifications = getting_notification_details()
    return render_template("template_error.html",notifications_info=notifications_info,number_of_notifications=number_of_notifications), 400

# If template has issues, this will be executed below

@app.errorhandler(TemplateError)
def handle_template_error(error):
    notifications_info,number_of_notifications = getting_notification_details()
    return render_template("template_error.html",notifications_info=notifications_info,number_of_notifications=number_of_notifications), 500

# Function which will retrieve the notifications in reverse order and the number of notifications. Those two things will be returned	
def getting_notification_details():
	notifications_info = db.forum_database.NotificationList.find().sort('_id', -1)
	number_of_notifications = db.forum_database.NotificationList.count_documents({'username': session.get("name"), 'seen': False})

	return notifications_info,number_of_notifications

# Check if users are mutually following each other

def mutually_following(student_profile_email):

	# Retrieve the information from the person who the user wants to chat with
	other_user_details = db.forum_database.RegLoginList.find({"email": student_profile_email })

	# Iterate through the other user's details and get the list of following and followers to see if they are mutually following
	# each other

	for document in other_user_details:
		list_of_followers = document["list_of_followers"]
		list_of_following = document["list_of_following"]

	# If they are mutually following each other, return True

	if session.get("name") in list_of_followers and session.get("name") in list_of_following:
		return True
	
	# Otherwise, return False

	else:
		return False

@app.route('/download_evidence/<filename>')
def download_evidence(filename):
    path = os.path.join("static/", filename)
    return send_file(path, as_attachment=True)

@app.route('/all_users_posts/<other_student_email>')
def all_users_posts(other_student_email):
	print(other_student_email)

	notifications_info,number_of_notifications = getting_notification_details()

	other_users_posts = db.forum_database.ForumPostCollection.find()
	other_users_replies = list(db.forum_database.ForumPostCollection.find({}))
	other_users_liked = list(db.forum_database.ForumPostCollection.find({}))

	other_users_likes = db.forum_database.NotificationList.find()

	return render_template("show_users_posts.html",other_users_posts=other_users_posts, other_student_email=other_student_email, other_users_replies=other_users_replies,other_users_liked=other_users_liked ,other_users_likes=other_users_likes,notifications_info=notifications_info,number_of_notifications=number_of_notifications)

# Route for homepage, which will present all of the subforums

@app.route('/')
def home():
	subforum_info = db.forum_database.SubforumList.find()
	notifications_info,number_of_notifications = getting_notification_details()
	return render_template("home.html", subforum_info=subforum_info, notifications_info=notifications_info,number_of_notifications=number_of_notifications)

@app.route('/faq')
def faq():
	notifications_info,number_of_notifications = getting_notification_details()
	return render_template("faq.html",notifications_info=notifications_info,number_of_notifications=number_of_notifications)

# Route that will render the specific subforum

@app.route('/visit_subforum/<subforum_name>')
def visit_subforum(subforum_name):
	collection_info = db.forum_database.ForumPostCollection.find().sort('time_stamp_when_post_created', -1)

	date_and_time_post_created = datetime.now()
		
	formatted_date_and_time_post_created = date_and_time_post_created.strftime("%d/%m/%Y %H:%M:%S")

	notifications_info,number_of_notifications = getting_notification_details()
	
	return render_template("subforum.html", subforum_name=subforum_name ,formatted_date_and_time_post_created=formatted_date_and_time_post_created, collection_info=collection_info,notifications_info=notifications_info,number_of_notifications=number_of_notifications)


# Route for register account which allows the user to register

@app.route('/register_account', methods =["GET", "POST"])
def register_account():
	if not session.get("name"):
		if request.method == "POST":
			fname = request.form.get("first_name")
			lname = request.form.get("last_name")
			email = request.form.get("email_address_for_register")
			passwd = request.form.get("user_password_for_register")
			bio = request.form.get("bio")
			profile_pic = request.files['profile_picture_for_register']

			if recaptcha.verify():
				if db.forum_database.RegLoginList.find_one({"email": {"$eq": email}}):
					return redirect("/register_account")
				else:
					encrypted_password = generate_password_hash(passwd)

					saving_profile_picture = secure_filename(profile_pic.filename)

					if profile_pic.filename == "":
						saving_profile_picture = secure_filename('360_F_346839683_6nAPzbhpSkIpb8pmAwufkC7c5eD7wYws.jpg')
					else:
						profile_pic.save(os.path.join("static/", saving_profile_picture))

					date_registered = date.today()

					date_registered = date_registered.strftime("%d/%m/%Y")

					db.forum_database.RegLoginList.insert_one({"first_name": fname, "last_name":lname, "email":email, "user_type":'normal' ,"password": encrypted_password, "bio": bio ,"profile_picture_link": saving_profile_picture,'user_registered': date_registered, "list_of_followers": [], "number_of_followers":0, "list_of_following": [], "number_of_following":0})
					
					session["name"] = request.form.get("email_address_for_register")

					session.permanent = True
					
					return redirect("/student_profile")
			else:
				return redirect("/register_account")
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

			for document in db.forum_database.RegLoginList.find():
				if email_for_login == document["email"]:
					if check_password_hash(document["password"],password_for_login):
						session["name"] = request.form.get("email_address_for_login")
						session.permanent = True
						db.forum_database.RegLoginList.update_one(
							{ 'email': request.form.get("email_address_for_login") },
							{ "$set": { 'last_seen': 'Online' } }
						)
						return redirect("/student_profile")
			flash('Invalid email or password. Please try again.')
			return redirect("/login_account")
		else:
			return render_template("Login.html")
	else:
		return "You are already logged in"

# Route created so that the user can logout when they want to

@app.route('/logout')
def logout():
	if session.get("name"):

		db.forum_database.RegLoginList.update_one(
			{ 'email': session.get("name") },
			{ "$set": { 'last_seen': datetime.now() } }
		)

		session["name"] = None
		return redirect("/login_account")
	else:
		return 'Cannot logout when you are not logged in'

# Route created for student profile

@app.route('/student_profile')
def student_profile():
	for document in db.forum_database.RegLoginList.find():
		if document["email"] == session["name"]:
			notifications_info,number_of_notifications = getting_notification_details()

			number_of_posts = db.forum_database.ForumPostCollection.count_documents({ 'author_of_post': document["email"] })

			number_of_comments = db.forum_database.ForumPostCollection.aggregate([
				{ "$unwind": "$comments" },
				{ "$group": {
					"_id": "$_id",
					"count": { "$sum": { "$cond": [{ "$eq": ["$comments.author_of_post", document["email"]] }, 1, 0] } }
				}},
				{ "$group": {
					"_id": None,
					"total_number_of_posts_and_comments": { "$sum": "$count" }
				}}
			])

			total_number_of_posts_and_comments = 0
			for element in number_of_comments:
				total_number_of_posts_and_comments = element["total_number_of_posts_and_comments"]
				break
			
			# Adding the number of posts and number of comments and putting them together

			total_number_of_posts_and_comments += number_of_posts

			user_details = db.forum_database.RegLoginList.find_one({"email": {"$eq": document["email"]}})

			student_name = user_details["first_name"] + " " + user_details["last_name"]

			return render_template("student_profile.html", document = document, notifications_info=notifications_info, number_of_notifications=number_of_notifications,total_number_of_posts_and_comments=total_number_of_posts_and_comments,student_name=student_name)

# Route created to view a profile of a student

@app.route('/viewing_profile/<student_profile_email>')
def viewing_profile(student_profile_email):
	for document in db.forum_database.RegLoginList.find():
		if document["email"] == student_profile_email:
			notifications_info,number_of_notifications = getting_notification_details()

			number_of_posts = db.forum_database.ForumPostCollection.count_documents({ 'author_of_post': document["email"] })

			number_of_comments = db.forum_database.ForumPostCollection.aggregate([
				{ "$unwind": "$comments" },
				{ "$group": {
					"_id": "$_id",
					"count": { "$sum": { "$cond": [{ "$eq": ["$comments.author_of_post", document["email"]] }, 1, 0] } }
				}},
				{ "$group": {
					"_id": None,
					"total_number_of_posts_and_comments": { "$sum": "$count" }
				}}
			])

			total_number_of_posts_and_comments = 0
			for element in number_of_comments:
				total_number_of_posts_and_comments = element["total_number_of_posts_and_comments"]
				break
			
			# Adding the number of posts and number of comments and putting them together

			total_number_of_posts_and_comments += number_of_posts

			user_details = db.forum_database.RegLoginList.find_one({"email": {"$eq": document["email"]}})

			student_name = user_details["first_name"] + " " + user_details["last_name"]

			return render_template("student_profile.html", document = document, notifications_info=notifications_info, number_of_notifications=number_of_notifications,total_number_of_posts_and_comments=total_number_of_posts_and_comments,student_name=student_name)

# Route created for changing profile picture

@app.route('/changing_profile_picture', methods =["GET", "POST"])
def changing_profile_picture():

	profile_picture = request.files['change_profile_picture_file_upload']
	changing_profile_picture = secure_filename(profile_picture.filename)
	profile_picture.save(os.path.join("static/", changing_profile_picture))
	
	db.forum_database.RegLoginList.update_one(
		{ 'email': session.get("name") },
		{ "$set": { 'profile_picture_link': changing_profile_picture } }
	)

	return redirect("/student_profile")


# Route created to render the forgot password html template

@app.route('/render_forgot_password_template', methods =["GET", "POST"])
def render_forgot_password_template():
	notifications_info,number_of_notifications = getting_notification_details()
	return render_template("forgot_password.html", notifications_info=notifications_info, number_of_notifications=number_of_notifications)

# Route created to update the password of the user

@app.route('/forgot_password', methods =["GET", "POST"])
def forgot_password():
	pwd_reset = request.form.get("password_reset")
	confirm_pwd_reset = request.form.get("confirm_password_reset")

	encrypted_pwd = generate_password_hash(pwd_reset)

	if pwd_reset == confirm_pwd_reset:
		db.forum_database.RegLoginList.update_one(
			{ 'email': session.get("name") },
			{ "$set": { 'password': encrypted_pwd } }
		)
	return redirect("/student_profile")

# Route for rendering the forum post template, which allows user to create a post

@app.route('/render_forum_post/<subforum_name>', methods =["GET", "POST"])
def render_forum_post(subforum_name):
	if session.get("name"):
		notifications_info,number_of_notifications = getting_notification_details()
		return render_template("forum_post.html", subforum_name=subforum_name,notifications_info=notifications_info, number_of_notifications=number_of_notifications)
	elif not session.get("name"):
		collection_info = db.forum_database.ForumPostCollection.find()
		return render_template("subforum.html", collection_info=collection_info)

# Route for viewing topic

@app.route('/view_topic/<_id>')
def view_topic(_id):
	user_info = db.forum_database.RegLoginList.find()
	another_user_info = db.forum_database.RegLoginList.find()
	another_user_info_2 = list(db.forum_database.RegLoginList.find())

	for document in db.forum_database.ForumPostCollection.find():
		if str(document["_id"]) == _id:
			post_title = document['title_of_post']
			content_post = document['content_of_post']
			subforum_name = document['subforum']
			collection_info = list(db.forum_database.ForumPostCollection.find())

			for user in user_info:
				if user['email'] == document['author_of_post']:
					registration_date_user = user['user_registered']
					break
			notifications_info,number_of_notifications = getting_notification_details()
			return render_template("view_forum_post.html", _id=_id ,registration_date_user=registration_date_user, another_user_info=another_user_info, another_user_info_2=another_user_info_2 ,user_info=user_info, post_title=post_title ,content_post = content_post, collection_info=collection_info,notifications_info=notifications_info, number_of_notifications=number_of_notifications,subforum_name=subforum_name)

# Route for rendering template that allows the user to re-enter the information that they want to update

@app.route('/edit_topic/<id_edit>')
def edit_topic(id_edit):
	for document in db.forum_database.ForumPostCollection.find():
		if str(document["_id"]) == id_edit:
			subforum_name = document["subforum"]
			notifications_info,number_of_notifications = getting_notification_details()
			return render_template("update_post.html", document=document ,id_edit=id_edit, notifications_info=notifications_info, number_of_notifications=number_of_notifications,subforum_name=subforum_name)

# Route for editing the topic in the database

@app.route('/edit_forum_topic/<id_edit>', methods =["GET", "POST"])
def edit_forum_topic(id_edit):

	subforum_name = request.form.get("name_of_subforum")
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

	return redirect("/visit_subforum/" + subforum_name)

# Route for deleting a topic

@app.route('/delete_topic/<id_delete>')
def delete_topic(id_delete):
	# First getting the subforum name so it can redirect to it after the post is deleted
	topic_to_delete = db.forum_database.ForumPostCollection.find_one({"_id": ObjectId(id_delete) })
	subforum_name = topic_to_delete["subforum"]

	# Removing the post from the subforum
	db.forum_database.ForumPostCollection.delete_one( {"_id": ObjectId(id_delete)} )

	return redirect("/visit_subforum/" + subforum_name)

# Route for like post functionality

@app.route('/like_post/<like_post_id>')
def like_post(like_post_id):

	for document in db.forum_database.ForumPostCollection.find():
		if str(document["_id"]) == like_post_id:
			if session.get("name") == document["author_of_post"]:

				subforum_name = document["subforum"]

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
				return redirect("/visit_subforum/" + subforum_name)
			
			else:
				if session.get("name") not in document["all_users_who_liked_post"] and session.get("name") != None:

					subforum_name = document["subforum"]

					db.forum_database.ForumPostCollection.update_one(
						{ '_id':  ObjectId(like_post_id) },
						{ "$inc": { 'number_of_likes':  1} }
					)

					db.forum_database.ForumPostCollection.update_one(
						{ '_id':  ObjectId(like_post_id) },
						{ "$push": { 'all_users_who_liked_post': session.get("name") } }
					)

					notification_content = session.get("name") + " liked your post : " + document["title_of_post"]
					db.forum_database.NotificationList.insert_one({"notification_type":'like' ,"forum_post_id":like_post_id,"username":document["author_of_post"],"username_of_follower":session.get("name"),"content":notification_content,"seen":False })
					return redirect("/visit_subforum/" + subforum_name)
	return redirect("/login_account")


# Route for dislike post functionality

@app.route('/dislike_post/<dislike_post_id>')
def dislike_post(dislike_post_id):

	for document in db.forum_database.ForumPostCollection.find():
		if str(document["_id"]) == dislike_post_id:

			if session.get("name") == document["author_of_post"]:

				subforum_name = document["subforum"]

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
				return redirect("/visit_subforum/" + subforum_name)
			
			else:
				if session.get("name") not in document["all_users_who_disliked_post"] and session.get("name") != None:

					subforum_name = document["subforum"]

					db.forum_database.ForumPostCollection.update_one(
						{ '_id':  ObjectId(dislike_post_id) },
						{ "$inc": { 'number_of_dislikes':  1} }
					)

					db.forum_database.ForumPostCollection.update_one(
						{ '_id':  ObjectId(dislike_post_id) },
						{ "$push": { 'all_users_who_disliked_post': session.get("name") } }
					)
					
					return redirect("/visit_subforum/" + subforum_name)


	return redirect("/login_account")

# Route for liking a reply

@app.route('/like_a_reply/<reply_id>', methods =["GET", "POST"])
def like_a_reply(reply_id):

	reply_id = int(reply_id)

	db.forum_database.ForumPostCollection.update_one(
		{ "comments.id": reply_id, "comments.list_of_users_who_liked": { "$nin": [session.get("name")] } },
		{ "$push": { "comments.$.list_of_users_who_liked": session.get("name") }, "$inc": { "comments.$.number_of_likes_for_reply": 1 } }
	)

	like_reply_document = db.forum_database.ForumPostCollection.find_one({"comments.id": reply_id })

	subforum_name = like_reply_document['subforum']

	return redirect('/visit_subforum/' + subforum_name)

# Route for disliking a reply

@app.route('/dislike_a_reply/<reply_id>', methods =["GET", "POST"])
def dislike_a_reply(reply_id):

	reply_id = int(reply_id)

	db.forum_database.ForumPostCollection.update_one(
		{ "comments.id": reply_id, "comments.list_of_users_who_disliked": { "$nin": [session.get("name")] } },
		{ "$push": { "comments.$.list_of_users_who_disliked": session.get("name") }, "$inc": { "comments.$.number_of_dislikes_for_reply": 1 } }
	)

	dislike_reply_document = db.forum_database.ForumPostCollection.find_one({"comments.id": reply_id })

	subforum_name = dislike_reply_document['subforum']

	return redirect('/visit_subforum/' + subforum_name)

# Route that will insert the forum post into the database, remove it completely, or send it to the admin dashboard

@app.route('/forum_post', methods =["GET", "POST"])
def forum_post():
	if session.get("name"):
		subforum_name = request.form.get("name_of_subforum")
		title = request.form.get("title_of_post")
		content = request.form.get("post_content")
		date_and_time_post_created = datetime.now()
		formatted_date_and_time_post_created = date_and_time_post_created.strftime("%d/%m/%Y %H:%M:%S")

		# Complexity implemented
		forum_post = content.lower()

		forum_post = forum_post.translate(str.maketrans('', '', string.punctuation))

		tokenization_of_forum_post = nltk.word_tokenize(forum_post)

		forum_post_tokenized_and_without_stop_words = []

		for word in tokenization_of_forum_post:
			if word not in stopwords.words('english'):
				forum_post_tokenized_and_without_stop_words.append(word)

		words_lemmatized = []

		for word, tag in pos_tag(forum_post_tokenized_and_without_stop_words):
			lemma = lemmatizer.lemmatize(word, tag_map[tag[0]])
			words_lemmatized.append(lemma)

		suspicious_and_nonsuspicious_words = pd.read_csv(r'Suspicious Communication on Social Platforms.csv')

		# Preprocessing : Cleaning the data so that I get the best form of it

		suspicious_and_nonsuspicious_words['comments'] = suspicious_and_nonsuspicious_words['comments'].str.lower() # turn all text into lowercase
		suspicious_and_nonsuspicious_words['comments'] = suspicious_and_nonsuspicious_words['comments'].str.replace('[^\w\s]','',regex = True) # remove character that is not a word character or whitespace
		suspicious_and_nonsuspicious_words['comments'] = suspicious_and_nonsuspicious_words['comments'].str.replace('\d+','', regex = True) # removes digits from data
		suspicious_and_nonsuspicious_words['comments'] = suspicious_and_nonsuspicious_words.apply(lambda row: nltk.word_tokenize(row['comments']), axis=1) # tokenizing the data so the sentence is divided into words

		suspicious_and_nonsuspicious_words_to_string = suspicious_and_nonsuspicious_words['comments'].astype(str)

		# Training and testing code

		X_train, X_test, y_train, y_test = train_test_split(suspicious_and_nonsuspicious_words_to_string, suspicious_and_nonsuspicious_words['tagging'], test_size=0.6, random_state=42) # splitting data into training and testing

		vectorizer = CountVectorizer(stop_words='english', ngram_range=(1, 2))
		X_train_vec = vectorizer.fit_transform(X_train)
		X_test_vec = vectorizer.transform(X_test)


		# vectorizing the post from the forum to see whether it is suspicious or not
		user_forum_post_vectorized = vectorizer.transform([" ".join(words_lemmatized)])

		# Training Naive Bayes Classifier

		nb = MultinomialNB()
		nb.fit(X_train_vec, y_train)

		# Evaluate the performance of the model
		y_pred = nb.predict(X_test_vec)

		probabilities = nb.predict_proba(user_forum_post_vectorized)[0]

		print(probabilities[1])
		if probabilities[1] > 0.5 and probabilities[1] < 0.8:

			db.forum_database.SuspiciousPostsList.insert_one({"subforum":subforum_name, "author_of_post":session.get("name"), "title_of_post": title, "content_of_post": content, "time_stamp_when_post_created": formatted_date_and_time_post_created})

		elif probabilities[1] >= 0.8:
			return "This post has not been posted as it has been detected as suspicious"
		else:
			db.forum_database.ForumPostCollection.insert_one({"subforum":subforum_name, "author_of_post":session.get("name"), "title_of_post": title, "content_of_post": content, "number_of_likes": 0, "number_of_dislikes": 0, "user_liked_own_post": False, "user_disliked_own_post": False, "all_users_who_liked_post": [], "all_users_who_disliked_post": [], "time_stamp_when_post_created": formatted_date_and_time_post_created, "comments":[]})

		print("Accuracy:", accuracy_score(y_test, y_pred) * 100)
		print("Precision:", precision_score(y_test, y_pred, pos_label=1))
		print("Recall:", recall_score(y_test, y_pred, pos_label=1))
		print("F1 score:", f1_score(y_test, y_pred, pos_label=1))

		return redirect('/visit_subforum/' + subforum_name)
	elif not session.get("name"):
		return redirect('/visit_subforum/' + subforum_name)

# Route that contains functionality that follows/unfollows a user

@app.route('/follow_user/<student_profile_email>', methods =["GET", "POST"])
def follow_user(student_profile_email):
	if session.get("name"):
		follow_button = request.form.get("follow_button");
		
		if follow_button == "Follow":
			db.forum_database.RegLoginList.update_one(
				{ 'email': student_profile_email },
				{ "$push": { 'list_of_followers': session.get("name") } }
			)

			user_collection = db.forum_database.RegLoginList.find_one({ 'email': student_profile_email })
			number_of_followers = len(user_collection["list_of_followers"])

			db.forum_database.RegLoginList.update_one(
				{ 'email': student_profile_email },
				{ "$set": { 'number_of_followers':  number_of_followers } }
			)

			db.forum_database.RegLoginList.update_one(
				{ 'email': session.get("name") },
				{ "$push": { 'list_of_following': student_profile_email } }
			)

			user_collection = db.forum_database.RegLoginList.find_one({ 'email': session.get("name") })
			number_of_following = len(user_collection["list_of_following"])

			db.forum_database.RegLoginList.update_one(
				{ 'email': session.get("name") },
				{ "$set": { 'number_of_following':  number_of_following } }
			)

			# Add in notifications database
			notification_content = session.get("name") + " followed you"
			db.forum_database.NotificationList.insert_one({"notification_type":'follow',"username":student_profile_email,"username_of_follower":session.get("name"),"content":notification_content,"seen":False })

		elif follow_button == "Following":
			db.forum_database.RegLoginList.update_one(
				{ 'email': student_profile_email },
				{ "$pull": { 'list_of_followers': session.get("name") } }
			)

			user_collection = db.forum_database.RegLoginList.find_one({ 'email': student_profile_email })
			number_of_followers = len(user_collection["list_of_followers"])

			db.forum_database.RegLoginList.update_one(
				{ 'email': student_profile_email },
				{ "$set": { 'number_of_followers':  number_of_followers } }
			)

			db.forum_database.RegLoginList.update_one(
				{ 'email': session.get("name") },
				{ "$pull": { 'list_of_following': student_profile_email } }
			)

			user_collection = db.forum_database.RegLoginList.find_one({ 'email': session.get("name") })
			number_of_following = len(user_collection["list_of_following"])

			db.forum_database.RegLoginList.update_one(
				{ 'email': session.get("name") },
				{ "$set": { 'number_of_following':  number_of_following } }
			)

		return redirect('/viewing_profile/' + student_profile_email)
	elif not session.get("name"):
		return redirect('/login_account')


# Route to redirect to the list of followers page

@app.route('/list_of_followers/<student_email>', methods =["GET", "POST"])
def list_of_followers(student_email):
	if session.get("name"):
		registration_info = db.forum_database.RegLoginList.find()
		registration_info_for_follower = list(db.forum_database.RegLoginList.find({}))

		notifications_info,number_of_notifications = getting_notification_details()
		
		return render_template("list_of_followers.html", student_email=student_email, registration_info=registration_info, notifications_info=notifications_info, number_of_notifications=number_of_notifications,registration_info_for_follower=registration_info_for_follower)
	elif not session.get("name"):
		return redirect('/login_account')

# Route to redirect to the list of following page

@app.route('/list_of_following/<student_email>', methods =["GET", "POST"])
def list_of_following(student_email):
	if session.get("name"):
		registration_info = db.forum_database.RegLoginList.find()
		registration_info_for_following = list(db.forum_database.RegLoginList.find({}))

		db.forum_database.NotificationList.update_many({'username': session.get("name")}, {'$set': {'seen': True}})
		notifications_info,number_of_notifications = getting_notification_details()
		return render_template("list_of_following.html", student_email=student_email, registration_info=registration_info, notifications_info=notifications_info, number_of_notifications=number_of_notifications,registration_info_for_following=registration_info_for_following)
	elif not session.get("name"):
		return redirect('/login_account')

# Route that will add the comment into the comments section of a particular post

@app.route('/reply_to_the_post/<post_id>', methods =["GET", "POST"])
def reply_to_the_post(post_id):
	if request.method == "POST":
		reply_content = request.form.get("reply_content")

	date_and_time_of_reply = datetime.now()
		
	date_and_time_of_reply_formatted = date_and_time_of_reply.strftime("%d/%m/%Y %H:%M:%S")


	highest_reply_id = 0
	for document in db.forum_database.ForumPostCollection.find():
		for obj in document["comments"]:
			if "id" in obj:
				highest_reply_id = max(highest_reply_id, obj["id"])

	db.forum_database.ForumPostCollection.update_one(
		{ '_id': ObjectId(post_id) },
		{ "$push": { 'comments': ({ 'id':highest_reply_id + 1,"author_of_post":session.get("name"), "content_of_post": reply_content, "timestamp_for_reply":date_and_time_of_reply_formatted, "number_of_likes_for_reply":0, "number_of_dislikes_for_reply":0 }) } }
	)

	student = db.forum_database.ForumPostCollection.find_one({ '_id': ObjectId(post_id) })
	student_profile_email = student["author_of_post"]
	forum_post_title = student["title_of_post"]

	# Add in notifications database
	notification_content = session.get("name") + " has replied to your post : " + forum_post_title
	db.forum_database.NotificationList.insert_one({"notification_type":'reply',"forum_post_id":post_id,"username":student_profile_email,"username_of_follower":session.get("name"),"content":notification_content,"seen":False})

	return redirect('/view_topic/' + post_id)

# Counts the number of notifications that the user has seen

@app.route('/update_notification_count', methods =["GET", "POST"])
def update_notification_count():
	if request.method == "POST":
		db.forum_database.NotificationList.update_many({'username': session.get("name")}, {'$set': {'seen': True}})
		number_of_notifications = db.forum_database.NotificationList.count_documents({'username': session.get("name"), 'seen': False})
		return jsonify(number_of_notifications=number_of_notifications)
	
# Edit bio functionality

@app.route('/edit_bio/<id_bio>', methods =["GET", "POST"])
def edit_bio(id_bio):

	bio_to_edit = request.form.get("bio_input")

	db.forum_database.RegLoginList.update_one(
		{ '_id':  ObjectId(id_bio) },
		{ "$set": { 'bio': bio_to_edit } }
	)

	return redirect("/student_profile")

# Retrieve messages in chat app so they are displayed in real time

@app.route('/retrieve_messages/<student_profile_email>')
def retrieve_messages(student_profile_email):
	messages = db.forum_database.MessageList.find({"participants": {"$all": [session.get("name"), student_profile_email]}})

	message_list = []

	for message in messages:

		for individual_message in message["messages"]:

			message_dict = {

				"content" : individual_message["content"],
				"timestamp" : individual_message["timestamp"],
				"recipient_email" : individual_message["recipient_email"],
				"recipient_name" : individual_message["recipient_name"],
				"sender_email" : individual_message["sender_email"],
				"sender_name" : individual_message["sender_name"]

			}

			message_list.append(message_dict)

	return jsonify(message_list)

# Render admin dashboard template page

@app.route('/render_admin_dashboard', methods =["GET", "POST"])
def render_admin_dashboard():
	suspicious_posts = db.forum_database.SuspiciousPostsList.find()
	reported_users = db.forum_database.ReportUserList.find()
	notifications_info,number_of_notifications = getting_notification_details()
	return render_template("admin_dashboard.html",notifications_info=notifications_info,number_of_notifications=number_of_notifications,suspicious_posts=suspicious_posts,reported_users=reported_users)

# Route that will remove the post that the admin wants to

@app.route('/admin_delete_post/<post_id>', methods =["GET", "POST"])
def admin_delete_post(post_id):
	db.forum_database.SuspiciousPostsList.delete_one({"_id": ObjectId(post_id) })
	return redirect("/render_admin_dashboard")

# Route that will approve a post that the admin wants to

@app.route('/admin_approve_post/<post_id>', methods =["GET", "POST"])
def admin_approve_post(post_id):
	suspicious_post = db.forum_database.SuspiciousPostsList.find({"_id": ObjectId(post_id) })

	for post in suspicious_post:
		db.forum_database.ForumPostCollection.insert_one(post)

		db.forum_database.SuspiciousPostsList.delete_one(post)

	return redirect("/render_admin_dashboard")

# Chat functionality route

@app.route('/render_message_user_template/<student_profile_email>', methods =["GET", "POST"])
def render_message_user_template(student_profile_email):

	# Call function to check if users are mutually following each other. Will return True or False
	mutual = mutually_following(student_profile_email)

	# If users are mutually following each other
	if mutual == True:

		user_details = db.forum_database.RegLoginList.find_one({"email": {"$eq": student_profile_email}})

		student_name = user_details["first_name"] + " " + user_details["last_name"]

		logged_in_user_details = db.forum_database.RegLoginList.find_one({"email": {"$eq": session.get("name")}})

		logged_in_user = logged_in_user_details["first_name"] + " " + logged_in_user_details["last_name"]

		notifications_info,number_of_notifications = getting_notification_details()

		message_list_info = db.forum_database.MessageList.find({"participants": {"$all": [session.get("name"), student_profile_email]}})

		if message_list_info.count() == 0:
			db.forum_database.MessageList.insert_one({"participants": [session.get("name"), student_profile_email], "messages": [] })

		user_last_seen = user_details.get("last_seen")

		if user_last_seen != "Online":

			current_time = datetime.now()
			time_diff = current_time - user_last_seen

			if time_diff.days > 0:
				if time_diff.days == 1:
					time_since_last_seen = '1 day ago'
				else:
					time_since_last_seen = f'{time_diff.days} days ago'

			elif time_diff.seconds < 60:
				time_since_last_seen = 'just now'

			elif time_diff.seconds < 3600:

				if time_diff.seconds >= 60 and time_diff.seconds <= 120:
					time_since_last_seen = '1 minute ago'
				else:
					minutes = time_diff.seconds // 60
					time_since_last_seen = f'{minutes} minutes ago'
				
			else:
				if time_diff.seconds >= 3600 and time_diff.seconds <= 7200:
					time_since_last_seen = '1 hour ago'

				else:
					hours = time_diff.seconds // 3600
					time_since_last_seen = f'{hours} hours ago'
		else:
			time_since_last_seen = 'Online'



		return render_template("message_user_template.html", notifications_info=notifications_info, number_of_notifications=number_of_notifications, message_list_info=message_list_info,user_details=user_details,student_name=student_name,student_profile_email=student_profile_email, logged_in_user=logged_in_user,time_since_last_seen=time_since_last_seen)
	
	# If users are NOT mutually following each other.
	else:
		return redirect("/")
		

def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')

    
@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
	print('received my event: ' + str(json))

	msg = json.get('message_sent')
	sender_email_address = json.get('sender_email_address')
	sender_name = json.get('logged_in_user')
	recipient_email_address = json.get('recipient_email')
	recipient_name = json.get('recipient_name')


	specific_conversation = db.forum_database.MessageList.find_one({'participants': {'$all': [sender_email_address, recipient_email_address]}})

	message_sent_time = datetime.now()

	message_sent_time_in_str = message_sent_time.strftime("%H:%M %p, %d/%m/%Y")

	new_message = {
		'content': msg,
		'timestamp': message_sent_time_in_str,
		'recipient_email': recipient_email_address,
		'recipient_name': recipient_name,
		'sender_email': sender_email_address,
		'sender_name': sender_name
	}
	if specific_conversation is not None:
		specific_conversation['messages'].append(new_message)

		db.forum_database.MessageList.update_one({'_id': specific_conversation['_id']}, {'$set': {'messages': specific_conversation['messages']}})

	socketio.emit('my response', json, callback=messageReceived)

@app.route('/render_report_user_template/<other_student_email>', methods =["GET", "POST"])
def render_report_user_template(other_student_email):
	if session.get("name"):
		notifications_info,number_of_notifications = getting_notification_details()
		return render_template("report_user.html",notifications_info=notifications_info,number_of_notifications=number_of_notifications,other_student_email=other_student_email)
	else:
		return redirect("/login_account")
	
@app.route('/report_user', methods =["GET", "POST"])
def report_user():
	if session.get("name"):

		other_student_email = request.form.get("reported_user")
		reason_for_report = request.form.get("report_reason")
		report_content = request.form.get("report_content")
		evidence = request.files['evidence']

		saving_evidence = secure_filename(evidence.filename)

		if evidence.filename == "":
			saving_evidence = ""
		else:
			evidence.save(os.path.join("static/", saving_evidence))

		db.forum_database.ReportUserList.insert_one({'reported_user':other_student_email,'reporter':session.get("name"),'reason_for_report':reason_for_report,'description':report_content, 'evidence':saving_evidence})

		session['form_processed'] = True

		return redirect("/render_confirmation_report_user")
	else:
		return redirect("/login_account")


@app.route('/render_confirmation_report_user', methods =["GET", "POST"])
def render_confirmation_report_user():
	if session.get('form_processed'):
		session.pop('form_processed', None)
		notifications_info,number_of_notifications = getting_notification_details()
		return render_template("confirmation_of_report.html",notifications_info=notifications_info,number_of_notifications=number_of_notifications)
	else:
		return redirect("/")

if __name__ == '__main__':
	socketio.run(app, debug=True)