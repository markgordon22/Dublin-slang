import os
from functools import wraps
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env

app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)

"""login_required taken from Task Mini Project
used to add defensive programming to site for user safety and security"""


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # no "user" in session
        if "user" not in session:
            flash("You must log in to view this page! :(")
            return redirect(url_for("login"))
        # user is in session
        return f(*args, **kwargs)
    return decorated_function


# Home page rendering
@app.route("/")
@app.route("/home")
def home():
    return render_template("index.html")


"""get_word() words from database and displays them on the glossary
page of site """


@app.route("/get_words")
def get_words():
    words = list(mongo.db.words.find())
    return render_template("get_words.html", words=words)


"""user can add word from the add_word() with the word keys
and values in the word dictionary. the dictionary will
insert into the database via the insert_one()"""


@app.route("/add_word", methods=["GET", "POST"])
@login_required
def add_word():
    if request.method == "POST":
        word = {
            "category_name": request.form.get("category_name"),
            "word_name": request.form.get("word_name"),
            "word_def": request.form.get("word_def"),
            "definition_example": request.form.get("definition_example"),
            "created_by": session["user"]
        }
        mongo.db.words.insert_one(word)
        flash("your word has been added")
        return redirect(url_for("get_words"))

    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("add_word.html", categories=categories)


"""
Register() - first time users can make a profile
by inserting username and a password
"""


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


""" Logout() logs user out of session and then redirected to login page
once logged out """


@app.route("/logout")
@login_required
def logout():
    # remove user from session cookies
    flash("You have been logged out. See ye after pal!")
    session.pop("user")
    return redirect(url_for("login"))


"""Login() if user meets criteria for username and password
they're brought to their profile page unless they're
username and/or password is false they remian at the login page """


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user" not in session:
        # only if there isn't a current session["user"]
        if request.method == "POST":
            # check if username exists in db
            existing_user = mongo.db.users.find_one(
                {"username": request.form.get("username").lower()})

            if existing_user:
                # ensure hashed password matches user input
                if check_password_hash(
                        existing_user["password"], request.form.get(
                            "password")):
                        session["user"] = request.form.get(
                                "username").lower()
                        flash("Welcome, {}".format(
                                request.form.get("username")))
                        return redirect(url_for(
                                "profile", username=session["user"]))
                else:
                    # invalid password match
                    flash("Incorrect Username and/or Password")
                    return redirect(url_for("login"))

            else:
                # username doesn't exist
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        return render_template("login.html")

    # user is already logged-in, direct them to their profile
    return redirect(url_for("profile", username=session["user"]))


"""profile() to render user profile with variables words
and username. If session["user] is falsey then the user
will be redirected back to the login page"""


@app.route("/profile/<username>", methods=["GET", "POST"])
@login_required
def profile(username):
    if session["user"].lower() == username.lower():
        username = mongo.db.users.find_one(
            {"username": session["user"]})["username"]
        # finds words added by user:
        words = list(mongo.db.words.find({"created_by": session["user"]}))
        # if existing user display profile
        if session["user"]:
            return render_template("profile.html",
                                   username=username, words=words)
    return redirect(url_for("login"))


"""
delete_profile() gets the user's details from the database and
deletes it with the delete_one(). user is then directed to register page
"""


@app.route("/delete_profile")
def delete_profile():
    if 'user' not in session:
        return redirect(url_for("login"))
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    mongo.db.users.delete_one({"username": username})
    flash("Profile successfully deleted. Goodbye mate :(")
    session.pop("user")
    return render_template("register.html", username=username)


"""
The search function goes through words in the database where it will match
the query keyword and render the word on the glossary page
"""


@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    words = list(mongo.db.words.find({"$text": {"$search": query}}))
    return render_template("get_words.html", words=words)


""" edit word gets word from db and updates it accordingly
with the keys and values in edit_submission dictionary.
It then updates the database with the update() """


@app.route("/edit_word/<word_id>", methods=["GET", "POST"])
@login_required
def edit_word(word_id):
    word = mongo.db.words.find_one({"_id": ObjectId(word_id)})
    if not word or word['created_by'] != session['user']:
        return render_template("login.html")
    if request.method == "POST":
        edit_submission = {
            "category_name": request.form.get("category_name"),
            "word_name": request.form.get("word_name"),
            "word_def": request.form.get("word_def"),
            "definition_example": request.form.get("definition_example"),
            "created_by": session["user"]
        }
        mongo.db.words.update({"_id": ObjectId(word_id)}, edit_submission)
        flash("word Successfully Updated!")
        return redirect(url_for("get_words"))

    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("edit_word.html", word=word, categories=categories)


"""delete_word() removes word from database with the remove(). user is then
redirected to glossary page after """


@app.route("/delete_word/<word_id>")
@login_required
def delete_word(word_id):
    mongo.db.words.remove({"_id": ObjectId(word_id)})
    flash("word Successfully Deleted!")
    return redirect(url_for("get_words"))


"""lists categories from database and then renders
to the categories page with edit and
delete options for those respective categories"""


@app.route("/get_categories")
@login_required
def get_categories():
    categories = list(mongo.db.categories.find().sort("category_name", 1))
    return render_template("categories.html", categories=categories)


"""add a category with the add_category(). Solely for
admin when wishing to make a category """


@app.route("/add_category", methods=["GET", "POST"])
@login_required
def add_category():
    if request.method == "POST":
        category = {
            "category_name": request.form.get("category_name")
        }
        mongo.db.categories.insert_one(category)
        flash("New Category has been Added")
        return redirect(url_for("get_categories"))

    return render_template("add_category.html")


"""edit a category with the edit_category(). This again is solely for
admin """


@app.route("/edit_category/<category_id>", methods=["GET", "POST"])
@login_required
def edit_category(category_id):
    if request.method == "POST":
        send = {
            "category_name": request.form.get("category_name")
        }
        mongo.db.categories.update({"_id": ObjectId(category_id)}, send)
        flash("Category has been updated")
        return redirect(url_for("get_categories"))

    category = mongo.db.categories.find_one({"_id": ObjectId(category_id)})
    return render_template("edit_category.html", category=category)


"""delete a category to remove a category from database. This is solely for
admin """


@app.route("/delete_category/<category_id>")
@login_required
def delete_category(category_id):
    mongo.db.categories.remove({"_id": ObjectId(category_id)})
    flash("Category has been deleted")
    return redirect(url_for("get_categories"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)