from flask import Flask, render_template, flash, redirect, session, request
from model import connect_to_db, User, Card, Deck, CardDeck, Library, db
from collections import defaultdict
from sqlalchemy import func

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
    elif "@" not in email:
        flash("Please enter a valid email address.")
    else:
        new_user = User.create(email, password)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created! Please log in.")

    return render_template("login.html")

@app.route("/login")
def login_page():
    user = session.get("user_id")
    return render_template("login.html", user=user)

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
    return redirect("/login")
    
@app.route("/logout", methods=["POST"])
def logout():
    """Logging out a user"""
    session.clear()
    flash("Logged out succesfully")
    return redirect("/login")

@app.route("/library/<int:card_id>")
def show_card(card_id):
    card = Card.get_by_card_id(card_id)
    if not card:
        flash("Card not found.")
        return redirect("/")
    
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in to add cards to your decks.")
        return redirect("/")
    decks = Deck.show_decks(user_id).all()
    
    return render_template("individual_cards.html", card=card, decks=decks)

@app.route("/library")
def show_library():
    page = request.args.get('page', 1, type=int)
    per_page = 100
    pagination = Card.query.order_by(Card.card_id.asc()).paginate(page=page, per_page=per_page, error_out=False)
    cards = pagination.items
    return render_template("library.html", cards=cards, pagination=pagination)

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        search = request.form.get("search")
        page = 1
    else:
        search = request.args.get("search")
        page = request.args.get('page', 1, type=int)

    per_page = 50
    if search:
        search_cards = db.session.query(Card).filter(Card.name_front.ilike(f'%{search}%')).order_by(Card.card_id.asc())
    else:
        search_cards = db.session.query(Card).order_by(Card.card_id.asc())

    pagination = search_cards.paginate(page=page, per_page=per_page, error_out=False)
    cards = pagination.items
    return render_template("library.html", cards=cards, pagination=pagination, search=search)

@app.route("/filter", methods=["GET", "POST"])
def filter_cards():
    if request.method == "POST":
        search = request.form.get("search")
        selected_colors = request.form.getlist("color")
        selected_types = request.form.getlist("card_type")
    else:
        search = request.args.get("search")
        selected_colors = request.args.getlist("color")
        selected_types = request.args.getlist("card_type")

    filter_conditions = []

    if search:
        filter_conditions.append(Card.name_front.ilike(f"%{search}%"))

    if selected_colors:
        for color in selected_colors:
            color_key = {
                "Green": "{G}",
                "Black": "{B}",
                "Blue": "{U}",
                "Red": "{R}",
                "White": "{W}",
                "Colorless": "{C}"
            }.get(color, "")
            if color_key:
                filter_conditions.append(Card.mana_cost_front.ilike(f"%{color_key}%"))

    if selected_types:
        for card_type in selected_types:
            type_key = {
                "Creature": "Creature",
                "Sorcery": "Sorcery",
                "Instant": "Instant",
                "Enchantment": "Enchantment",
                "Artifact": "Artifact",
                "Planeswalker": "Planeswalker",
                "Battle — Siege": "Battle — Siege",
                "Land": "Land"
            }.get(card_type, "")
            if type_key:
                filter_conditions.append(Card.type_line_front.ilike(f"%{type_key}%"))

    if filter_conditions:
        filtered_cards = db.session.query(Card).filter(db.and_(*filter_conditions)).order_by(Card.card_id.asc())
    else:
        filtered_cards = db.session.query(Card).order_by(Card.card_id.asc())

    page = request.args.get('page', 1, type=int)
    per_page = 50
    pagination = filtered_cards.paginate(page=page, per_page=per_page, error_out=False)

    return render_template("library.html", cards=pagination.items, pagination=pagination, selected_colors=selected_colors, selected_types=selected_types, search=search)

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
    
    # Query to get all cards in the deck and count occurrences
    card_decks = db.session.query(
        CardDeck.card_id, func.count(CardDeck.card_id).label('count')
    ).filter(CardDeck.deck_id == deck_id).group_by(CardDeck.card_id).all()

    cards = []
    total_cards = 0
    cards_by_type = defaultdict(list)

    for card_id, count in card_decks:
        card = db.session.get(Card, card_id)
        total_cards += count
        card_type = card.type_line_front

        # Add card to the appropriate type list
        if "Creature" in card_type:
            cards_by_type["Creature"].append(card)
        elif "Sorcery" in card_type:
            cards_by_type["Sorcery"].append(card)
        elif "Instant" in card_type:
            cards_by_type["Instant"].append(card)
        elif "Enchantment" in card_type:
            cards_by_type["Enchantment"].append(card)
        elif "Artifact" in card_type:
            cards_by_type["Artifact"].append(card)
        elif "Planeswalker" in card_type:
            cards_by_type["Planeswalker"].append(card)
        elif "Battle" in card_type:
            cards_by_type["Battle — Siege"].append(card)
        elif "Land" in card_type:
            cards_by_type["Land"].append(card)

        # Add the card to the list with the count (optional, if you want to display counts)
        cards.append((card, count))

    return render_template("individual_deck.html", deck=deck, cards_by_type=cards_by_type, total_cards=total_cards)

@app.route("/deck/remove_card", methods=["POST"])
def remove_card():
    name_req = request.form.get("name").strip()
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
    existing_deck = Deck.get_by_name(name_req)

    if existing_deck:
        flash("A deck with this name already exists.")
        return redirect("/deck")

    new_deck = Deck.create(user_id=user_id, name=name_req)
    db.session.add(new_deck)
    try:
        db.session.commit()
        flash("Deck created successfully!")
    except Exception as e:
        db.session.rollback()
        print(f"Error creating deck: {e}")
        flash("Error creating deck.")

    return redirect("/deck")

@app.route("/delete_deck", methods=["POST"])
def delete_deck():
    user_id = session.get("user_id")
    if not user_id:
        flash("You need to be logged in to delete a deck.")
        return redirect("/login")
    
    name_req = request.form.get("name")
    existing_deck = Deck.get_by_name(name_req)

    if not existing_deck:
        flash("No deck exists with that name.")

    db.session.delete(existing_deck)
    flash(f"Deck {existing_deck.name} deleted sucesfully!")
    db.session.commit()
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