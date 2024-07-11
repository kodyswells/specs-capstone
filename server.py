from flask import Flask, render_template, flash, redirect, session, request
from model import connect_to_db, User, Card, Deck, CardDeck, Library, db

app = Flask(__name__)
app.secret_key = "DevTest"


@app.route("/")
def homepage ():
    return render_template('homepage.html')

@app.route("/users")
def users ():
    users = User.all_users()

    return render_template("users.html", users=users)

@app.route("/users", methods=["POST"])
def register_user():
    """Create a new user."""
    email = request.form.get("email")
    password = request.form.get("password")

    user = User.get_by_email(email)
    if user:
        flash("User already exists. Please log in.")
    else:
        new_user = User.create(email, password)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created! Please log in.")

    return redirect("/")

@app.route("/login", methods=["POST"])
def login():
    """Logging in as a user"""
    email = request.form.get("email")
    password = request.form.get("password")
    
    user = User.get_by_email(email)
    if user and User.verify_password(user.password_hash, user.salt, password):
        session["user_id"] = user.user_id
        flash("You have logged in successfully!")
        return redirect("/")
    else:
        flash("Invalid login information")
        return redirect("/")
    
@app.route("/logout", methods=["POST"])
def logout():
    """Logging out a user"""
    session.clear()
    flash("Logged out succesfully")
    return redirect("/")

if __name__ == "__main__":
    connect_to_db(app)
    app.run(host="localhost", port=5555, debug=True)