import os
from functools import wraps
from flask import (
    Flask, flash, render_template,
    redirect, g, request, session, url_for)
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


@app.route("/")
@app.route("/home")
def home():
    return render_template("index.html")


@app.route("/get_words")
def get_words():
    words = list(mongo.db.words.find())
    return render_template("get_words.html", words=words)


@app.route("/contact")
def contact():
    return render_template("contact.html")


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
        flash("your Word has been added")
        return redirect(url_for("get_words"))

    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("add_word.html", categories=categories)

          
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


@app.route("/logout")
@login_required
def logout():
    # remove user from session cookies
    flash("You have been logged out. See ye after pal!")
    session.pop("user")
    return redirect(url_for("login"))


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


@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    words = list(mongo.db.words.find({"$text": {"$search": query}}))
    return render_template("get_words.html", words=words)


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
        flash ("word Successfully Updated!")
        return redirect(url_for("get_words"))
        
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("edit_word.html", word=word, categories=categories)


@app.route("/delete_word/<word_id>")
@login_required
def delete_word(word_id):
    mongo.db.words.remove({"_id": ObjectId(word_id)})
    flash("word Successfully Deleted!")
    return redirect(url_for("get_words"))


@app.route("/get_categories")
@login_required
def get_categories():
    categories = list(mongo.db.categories.find().sort("category_name", 1))
    return render_template("categories.html", categories=categories)


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