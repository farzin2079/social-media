import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, imgtobi, bitoimg

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///informations.db")

@app.route("/")
@login_required
def index():
    """show posts"""
    user_id = session["user_id"]
    posts = db.execute("SELECT postguy, image, caption, id FROM posts ORDER BY id DESC")

    commentguy = db.execute("SELECT username FROM users WHERE id = ?", user_id)

    return render_template("index.html", posts=posts, commentguy=commentguy)

@app.route("/addpost", methods=["GET", "POST"])
@login_required
def addposts():
    """submit posts"""
    if (request.method == "POST"):
        # take username and add to post table
        user_id = session["user_id"]
        postguy = request.form.get("postguy")

        #take another elements of posts
        image = request.form.get("image")
        caption = request.form.get("caption")
        #make biannery code for image
        try:
            db.execute("INSERT INTO posts ( postguy, image, caption, user_id) VALUES (?,?,?,?)", postguy, image, caption, user_id)
            return redirect("/")
        except:
            return apology(postguy)
    else:
        return render_template("index.html")

@app.route("/page")
@login_required
def page():
    """Show self posts"""
    user_id = session["user_id"]
    posts = db.execute("SELECT image,caption,id FROM posts WHERE user_id = ?", user_id)

    return render_template("page.html", posts=posts)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""


    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):

            return apology("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):

            return apology("must provide password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):

            return apology("invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/delete", methods=["GET", "POST"])
@login_required
def delete():
    """delete self posts ERORR! try again"""
    if (request.method == "POST"):
        id = request.form.get("id")

        try:
            db.execute("DELETE FROM comments WHERE post_id = ?", id)
            db.execute("DELETE FROM posts WHERE id = ?", id)
            return redirect("/page")
        except:
            return apology("ERORR! (141)")

    else:
        return redirect("/page")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if (request.method == "POST"):
        username = request.form.get('username')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')
        phone_number = request.form.get("phone_number")

        if not username:
            return apology('Username is required!')
        elif not password:
            return apology('Password is required!')
        elif not confirmation:
            return apology('Password confirmation is required!')

        if password != confirmation:
            return apology('Passwords do not match!')

        hash = generate_password_hash(password)
        try :
            db.execute("INSERT INTO users (username,hash,phone_number) VALUES (?,?,?)", username, hash, phone_number)
            return redirect('/')
        except:
            return apology('Username has Already been registered!')

    else:
        return render_template("register.html")


@app.route("/post", methods=["GET", "POST"])
@login_required
def post():
    # select user_id who want addpost
    postguy = db.execute("SELECT username FROM users WHERE id =?", session["user_id"])
    return render_template("post.html", postguy=postguy)

@app.route("/addcomment", methods=["GET", "POST"])
@login_required
def addcomment():
     #add comment
    if (request.method == "POST"):
        commenttext = request.form.get("comment")
        commentguy = request.form.get("commentguy")
        post_id = request.form.get("post_id")
        try:
            db.execute("INSERT INTO comments (comment, commentguy, post_id) VALUES (?,?,?)", commenttext, commentguy, post_id)
            #show comments
            comments = db.execute("SELECT comment, commentguy FROM comments WHERE post_id = ?", post_id)
            posts = db.execute("SELECT image, postguy, caption FROM posts WHERE id = ?", post_id)
            return render_template("comment.html", comments=comments, posts=posts )
        except:
            return apology("ERORR!(198)")
    else:
        return redirect("/")
@app.route("/showcomments", methods=["GET", "POST"])
@login_required
def comments():
    #show comments
    post_id = request.form.get("post_id")

    comments = db.execute("SELECT comment, commentguy FROM comments WHERE post_id = ?", post_id)
    posts = db.execute("SELECT image, postguy, caption FROM posts WHERE id = ?", post_id)
    return render_template("comment.html", posts=posts, comments=comments )
