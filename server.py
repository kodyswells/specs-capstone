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
    
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in to add cards to your decks.")
        return redirect("/login")
    
    decks = Deck.show_decks(user_id).all()
    
    return render_template("individual_cards.html", card=card, decks=decks)

@app.route("/library")
def show_library():
    cards = Card.query.all()
    return render_template("library.html", cards=cards)

@app.route("/deck")
def all_decks():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in to see your decks.")
        return redirect("/")
    all_decks = Deck.show_decks(user_id)
    return render_template("decks.html", deck = all_decks)

@app.route("/deck/<int:deck_id>")
def show_cards_in_deck(deck_id):
    deck = db.session.get(Deck, deck_id)
    if not deck:
        flash("Deck not found")
        return redirect("/deck")
    
    card_decks = CardDeck.get_by_deck_id(deck_id)
    cards = [cd.card for cd in card_decks]
    
    return render_template("individual_deck.html", deck=deck, cards=cards)

@app.route("/deck/remove_card", methods=["POST"])
def remove_card():
    name_req = request.form.get("name").strip()  # Strip any leading/trailing whitespace
    deck_id = request.form.get("deck_id")
    quantity = int(request.form.get("quantity"))
   
    # Query to find the card entries within the specified deck
    card_deck_entries = db.session.query(CardDeck).join(Card).filter(
        CardDeck.deck_id == deck_id,
        db.func.lower(Card.name_front) == db.func.lower(name_req)
        ).limit(quantity).all()
    
    if card_deck_entries:
        for entry in card_deck_entries:
            print(f"Removing card: {entry.card}")
            db.session.delete(entry)
        
        db.session.commit()
        flash(f"Removed {len(card_deck_entries)} card(s) from the deck")
    else:
        print(f"No cards found in deck with name: '{name_req}'")
        flash("Card not found in the deck")

    return redirect(f"/deck/{deck_id}")

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
    if not card:
        flash("Card not found")
        return redirect(f"/library/{card_id}")

    deck_id = request.form.get("deck_id")
    deck = Deck.get_deck_id(deck_id)
    if not deck:
        flash("Deck not found")
        return redirect(f"/library/{card_id}")
    
    new_card = CardDeck.add_card(card_id=card.card_id, deck_id=deck.deck_id)
    db.session.add(new_card)
    db.session.commit()

    flash("Card added to deck.")
    return redirect(f"/library/{card_id}")


if __name__ == "__main__":
    connect_to_db(app)
    app.run(host="localhost", port=5555, debug=True)