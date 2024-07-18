from flask import Flask, render_template, flash, redirect, session, request
from model import connect_to_db, User, Card, Deck, CardDeck, Library, db

app = Flask(__name__)
app.secret_key = "DevTest"


@app.route("/")
def homepage ():
    return render_template('homepage.html')

@app.route("/users")
def users ():

    return render_template("users.html")

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

@app.route("/library/<int:card_id>")
def show_card(card_id):
    card = Card.get_by_card_id(card_id)
    if not card:
        flash("Card not found.")
        return redirect("/")
    return render_template("individual_cards.html", card=card)

@app.route("/deck")
def all_decks():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in to see your decks.")
    all_decks = Deck.show_decks(user_id)
    return render_template("decks.html", deck = all_decks)

@app.route("/create_deck", methods=["POST"])
def create_deck():
    user_id = session.get("user_id")
    if not user_id:
        flash("You need to be logged in to create a deck.")
        return redirect("/login")
    name_req = request.form.get("name")
    name = Deck.get_by_name(name_req)

    new_deck = Deck.create(user_id, name)
    db.session.add(new_deck)
    try:
        db.session.commit()
    except:
        print("error")
    flash("Deck created successfully!")
    return redirect("/deck")

@app.route("/library/<int:card_id>/add_card", methods=["POST"])
def add_card_to_deck(card_id):

    card = Card.get_by_card_id(card_id)

    name = request.form.get("name")
    deck = Deck.get_by_name(name)
    if not card:
        flash("Card not found")
        return redirect("/library/<int:card_id")
    
    new_card = CardDeck.add_card(card_id = card.card_id, deck_id= deck.deck_id)
    db.session.add(new_card)
    db.session.commit()
    flash("Card added to deck.")
    return redirect(f"/library/{card_id}")


if __name__ == "__main__":
    connect_to_db(app)
    app.run(host="localhost", port=5555, debug=True)