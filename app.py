import os
from flask import Flask, flash, render_template, redirect, request, session, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONOGO_DBNAME"] = os.environ.get("MONGO_DB")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/episode_review")
def get_episode_review():
    reviews = list(mongo.db.reviews.find())
    return render_template("episode-review.html", reviews=reviews)


@app.route("/signup", methods= ["GET", "POST"])
def signup():
    if request.method == "POST":
        # check id username already exists in database
        exisiting_user = mongo.db.users.find_one({"username": request.form.get("username").lower()})

        if exisiting_user:
            flash("Username already exists")
            return redirect(url_for("signup"))

        signup = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(signup)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Sign Up Successful")
        return redirect(url_for("profile", username=session["user"]))
    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one({"username": request.form.get("username").lower()})

        if existing_user:
            #ensure hashed password matches user input
            if check_password_hash(existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(request.form.get("username")))
                return redirect(url_for("profile", username=session["user"]))
            else:
                # invalid password match
                flash("incorrect Username and/or Password")
                return redirect(url_for("login"))
            
        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # grab the session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("profile.html", username=username)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # remove user from session cookies
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/manage_reviews", methods=["GET", "POST"])
def manage_reviews():
    if request.method == "POST":
        been_reviewed = "on" if request.form.get("been_reviewed") else "off"
        review = {
            "new_episode_review": request.form.get("new_episode_review"),
            "episode_to_review": request.form.get("episode_to_review"),
            "episode_review_description": request.form.get("episode_review_description"),
            "been_reviewed": been_reviewed,
            "due_date": request.form.get("due_date"),
            "created_by": session["user"]
        }
        mongo.db.reviews.insert_one(review)
        flash("Episode to be Reviewed has been Successfully Added.")
        return redirect(url_for("get_episode_review"))

    episodes = mongo.db.episodes.find().sort("new_episode_review", 1)
    return render_template("manage_reviews.html", episodes=episodes)


@app.route("/edit_reviews/<review_id>", methods=["GET", "POST"])
def edit_reviews(review_id):
    if request.method == "POST":
        been_reviewed = "on" if request.form.get("been_reviewed") else "off"
        submit = {
            "new_episode_review": request.form.get("new_episode_review"),
            "episode_to_review": request.form.get("episode_to_review"),
            "episode_review_description": request.form.get
            ("episode_review_description"),
            "been_reviewed": been_reviewed,
            "due_date": request.form.get("due_date"),
            "created_by": session["user"]
        }
        mongo.db.reviews.update({"_id": ObjectId(review_id)},submit)
        flash("Review has been Successfully Edited.")

    review = mongo.db.reviews.find_one({"_id": ObjectId((review_id))})
    episodes = mongo.db.episodes.find().sort("new_episode_review", 1)
    return render_template("edit_reviews.html", review=review,
                            episodes=episodes)


@app.route("/delete_reviews/<review_id>")
def delete_reviews(review_id):
    mongo.db.reviews.remove({"_id": ObjectId(review_id)})
    flash(("Review Successfully Deleted"))
    return redirect(url_for("get_episode_review"))

@app.route("/get_episodes")
def get_episodes():
    episodes = list(mongo.db.episodes.find().sort("new_episode_review", 1))
    return render_template("episodes.html", episodes=episodes)

@app.route("/add_episode", methods =["GET", "POST"])
def add_episode():
    if request.method == "POST":
        episode = {
            "new_episode_review": request.form.get("new_episode_review")
        }
        mongo.db.episodes.insert_one(episode)
        flash("New Episode Added")
        return redirect(url_for("get_episodes"))

    return render_template("add_episode.html")
    
@app.route("/edit_episode/<episode_id>", methods=["GET", "POST"])
def edit_episode(episode_id):
    if request.method == "POST":
        submit = {
            "new_episode_review": request.form.get("new_episode_review")
        }
        mongo.db.episodes.update({"_id": ObjectId(episode_id)}, submit)
        flash("Episode Successfully Updated")
        return redirect(url_for("get_episodes"))
    episode = mongo.db.episodes.find_one({"_id": ObjectId(episode_id)})
    return render_template("edit_episode.html", episode=episode)

@app.route("/delete_episode/<episode_id>")
def delete_episode(episode_id):
    mongo.db.episodes.remove({"_id": ObjectId(episode_id)})
    flash("Episode Successfully Deleted")
    return redirect(url_for("get_episodes"))

if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
