import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    """A User"""
    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement = True, primary_key = True, unique = True)
    email = db.Column(db.String, unique = True)
    password = db.Column(db.String)

    decks = db.relationship("Deck", backref="user", lazy=True)
    libraries = db.relationship("Library", backref="user", lazy=True)

    def __repr__(self):
        return f"<User user_id = {self.user_id}, email = {self.email}, password = {self.password}>"
    
class Card(db.Model):
    """A MTG Card"""
    __tablename__ = "cards"

    card_id = db.Column(db.Integer, autoincrement = True, primary_key = True, unique = True)
    name_front = db.Column(db.String, nullable = False)
    cmc_front = db.Column(db.Integer, nullable = False)
    type_line_front = db.Column(db.String, nullable = False)
    oracle_text_front = db.Column(db.Text, nullable = False)
    img_uri_small_front = db.Column(db.Text, nullable = False)
    img_uri_normal_front = db.Column(db.Text, nullable = False)
    name_back = db.Column(db.String)
    cmc_back = db.Column(db.Integer)
    type_line_back = db.Column(db.String)
    oracle_text_back = db.Column(db.Text)
    img_uri_small_back = db.Column(db.Text)
    img_uri_normal_back = db.Column(db.Text)

    libraries = db.relationship("Library", backref="card", lazy=True)
    card_decks = db.relationship("CardDeck", backref="card", lazy=True)

    def __repr__(self):
        return f"<Card card_id = {self.card_id}, name_front = {self.name_front}, cmc_front = {self.cmc_front}, type_line_front = {self.type_line_front}, oracle_text_front = {self.oracle_text_front}, img_uri_small_front = {self.img_uri_small_front}, img_uri_normal_front = {self.img_uri_normal_front}, name_back = {self.name_back}, cmc_back = {self.cmc_back}, type_line_back = {self.type_line_back}, oracle_text_back = {self.oracle_text_back}, img_uri_small_back = {self.img_uri_small_back}, img_uri_normal_back = {self.img_uri_normal_back}>"
    
class Deck(db.Model):
    """A users decks"""
    __tablename__ = "decks"

    deck_id = db.Column(db.Integer, autoincrement = True, primary_key = True, unique = True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))

    card_decks = db.relationship("CardDeck", backref="deck", lazy=True)

    def __repr__(self):
        return f"<Deck deck_id = {self.deck_id}, user_id = {self.user_id}>"
    
class CardDeck(db.Model):
    """Association table between Cards and Decks"""
    __tablename__ = "card_decks"

    card_deck_id = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True)
    card_id = db.Column(db.Integer, db.ForeignKey("cards.card_id"))
    deck_id = db.Column(db.Integer, db.ForeignKey("decks.deck_id"))

    def __repr__(self):
        return f"<CardDeck card_deck_id={self.card_deck_id}, card_id={self.card_id}, deck_id={self.deck_id}>"
    
class Library(db.Model):
    """A Users' Library"""
    __tablename__ = "libraries"

    library_id = db.Column(db.Integer, autoincrement = True, primary_key = True, unique = True)
    card_id = db.Column(db.Integer, db.ForeignKey("cards.card_id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))

    def __repr__(self):
        return f"<Library library_id = {self.library_id}, card_id = {self.card_id}, user_id = {self.user_id}>"

def connect_to_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["POSTGRES_URI"]
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)

    print("Connected to the db!")


if __name__ == "__main__":
    from server import app

    connect_to_db(app)