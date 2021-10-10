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
@app.route("/get_episode_review")
def get_episode_review():
    reviews = mongo.db.reviews.find()
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
        session["users"] = request.form.get("username").lower()
        flash("Sign Up Successful")
    return render_template("signup.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
