from flask import Flask, render_template, request, redirect, session
from werkzeug.utils import secure_filename
from pymongo import MongoClient
import os

app = Flask(__name__)
app.secret_key = "mysecretkey123"

# MONGO CONNECTION
client = MongoClient("mongodb://localhost:27017/")
db = client["blogDB"]
users = db.users
posts = db.posts

# IMAGE UPLOAD FOLDER
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# HOME PAGE
@app.route("/")
def home():
    return render_template("index.html")

# REGISTER PAGE
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        if users.find_one({"email": email}):
            return "Email already registered!"

        users.insert_one({
            "name": name,
            "email": email,
            "password": password
        })

        return redirect("/login")

    return render_template("register.html")

# LOGIN PAGE
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = users.find_one({"email": email, "password": password})

        if user:
            session["email"] = email
            return redirect("/dashboard")

        return "Invalid email or password"

    return render_template("login.html")

# DASHBOARD
@app.route("/dashboard")
def dashboard():
    if "email" not in session:
        return redirect("/login")

    total_posts = posts.count_documents({})
    total_views = 0

    return render_template(
        "dashboard.html",
        total_posts=total_posts,
        total_views=total_views
    )

# ADD POST
@app.route("/add", methods=["GET", "POST"])
def add_post():
    if "email" not in session:
        return redirect("/login")

    if request.method == "POST":
        title = request.form["title"]
        category = request.form["category"]
        content = request.form["content"]

        image_file = request.files["image"]
        filename = secure_filename(image_file.filename)
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        image_file.save(image_path)

        posts.insert_one({
            "title": title,
            "category": category,
            "content": content,
            "image": filename,
            "author": session["email"]
        })

        return redirect("/dashboard")

    return render_template("add.html")

@app.route("/myposts")
def myposts():
    if "email" not in session:
        return redirect("/login")

    user_posts = posts.find({"author": session["email"]})

    return render_template("myposts.html", posts=user_posts)

# ABOUT PAGE
@app.route("/about")
def about():
    return render_template("about.html")

# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# RUN
if __name__ == "__main__":
    app.run(debug=True)