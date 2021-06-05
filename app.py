import os
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

mongo  = PyMongo(app)


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
def add_word():
    if request.method == "POST":
        word = {
            "category_name": request.form.get("category_name"),
            "word_name": request.form.get("word_name"),
            "word_defintion": request.form.get("word_definition"),
            "definition_example": request.form.get("defintion_example"),
            "created_by": session["user"]
        }
        mongo.db.words.insert_one(word)
        flash("your Word has been added")
        return redirect(url_for("get_words"))

    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("add_word.html", categories=categories)



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                        session["user"] = request.form.get("username").lower()
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
            flash("Incorrect Username and/or Password!")
            return redirect(url_for("login"))

    return render_template("login.html")
          


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
def logout():
    # remove user from session cookie
    flash("You have successfully logged out")
    return redirect(url_for("login"))


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # grab the session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    return render_template("profile.html", username=username)


@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    words = list(mongo.db.words.find({"$text": {"$search": query}}))
    return render_template("get_words.html", words=words)


@app.route("/edit_word/<word_id>", methods=["GET", "POST"])
def edit_word(word_id):




if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
