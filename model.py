import os
from flask_sqlalchemy import SQLAlchemy
import scrypt

db = SQLAlchemy()

class User(db.Model):
    """A User"""
    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True)
    email = db.Column(db.String, unique=True)
    password_hash = db.Column(db.LargeBinary)
    salt = db.Column(db.String(32))

    decks = db.relationship("Deck", backref="user", lazy=True)
    libraries = db.relationship("Library", backref="user", lazy=True)

    def __repr__(self):
        return f"<User user_id={self.user_id}, email={self.email}>"

    @classmethod
    def create(cls, email, password):
        """Create and return a new user."""

        salt = os.urandom(16)
       
        password_hash = scrypt.hash(password, salt)
        salt_str = salt.hex()

        return cls(email=email, password_hash=password_hash, salt=salt_str)

    @staticmethod
    def verify_password(stored_hash, stored_salt, password):
        """Verify a stored password against one provided by user."""

        salt_bytes = bytes.fromhex(stored_salt)
        hashed_password = scrypt.hash(password, salt_bytes)
        return stored_hash == hashed_password

    @classmethod
    def get_by_id(cls, user_id):
        return db.session.query(cls).get(user_id)

    @classmethod
    def get_by_email(cls, email):
        return db.session.query(cls).filter(User.email == email).first()
    
class Card(db.Model):
    """A MTG Card"""
    __tablename__ = "cards"

    card_id = db.Column(db.Integer, autoincrement = True, primary_key = True, unique = True)
    name_front = db.Column(db.String, nullable = False)
    mana_cost_front = db.Column(db.String, nullable = True)
    cmc_front = db.Column(db.Integer, nullable = True)
    type_line_front = db.Column(db.String, nullable = False)
    oracle_text_front = db.Column(db.Text, nullable = False)
    img_uri_small_front = db.Column(db.Text, nullable = False)
    img_uri_normal_front = db.Column(db.Text, nullable = False)
    name_back = db.Column(db.String, nullable = True)
    mana_cost_back = db.Column(db.String, nullable = True)
    cmc_back = db.Column(db.Integer, nullable = True)
    type_line_back = db.Column(db.String, nullable = True)
    oracle_text_back = db.Column(db.Text, nullable = True)
    img_uri_small_back = db.Column(db.Text, nullable = True)
    img_uri_normal_back = db.Column(db.Text, nullable = True)

    libraries = db.relationship("Library", backref="card", lazy=True)
    card_decks = db.relationship("CardDeck", backref="card", lazy=True)

    def __repr__(self):
        return f"<Card card_id = {self.card_id}, name_front = {self.name_front}, cmc_front = {self.cmc_front}, type_line_front = {self.type_line_front}, oracle_text_front = {self.oracle_text_front}, img_uri_small_front = {self.img_uri_small_front}, img_uri_normal_front = {self.img_uri_normal_front}, name_back = {self.name_back}, cmc_back = {self.cmc_back}, type_line_back = {self.type_line_back}, oracle_text_back = {self.oracle_text_back}, img_uri_small_back = {self.img_uri_small_back}, img_uri_normal_back = {self.img_uri_normal_back}>"
    
    @classmethod
    def get_by_card_id(cls, card_id):
        return db.session.get(cls, card_id)
    
    @classmethod
    def get_by_name(cls, name):
        print(f"Querying card with name: '{name}'")
        return db.session.query(cls).filter(db.func.lower(cls.name_front) == db.func.lower(name.strip())).first()

class Deck(db.Model):
    """A users decks"""
    __tablename__ = "decks"

    deck_id = db.Column(db.Integer, autoincrement = True, primary_key = True, unique = True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    name = db.Column(db.String, nullable = False)

    card_decks = db.relationship("CardDeck", backref="deck", lazy=True)

    def __repr__(self):
        return f"<Deck deck_id = {self.deck_id}, user_id = {self.user_id}>"
    
    @classmethod
    def create(cls, user_id, name):
        return cls(user_id=user_id, name=name)
    
    @classmethod
    def show_decks(cls, user_id):
        return db.session.query(cls).filter(Deck.user_id == user_id)
    
    @classmethod
    def get_deck_id(cls, deck_id):
        return cls(deck_id = deck_id)
    
    @classmethod
    def get_by_name(cls, name):
        return db.session.query(cls).filter_by(name=name).first()
    
class CardDeck(db.Model):
    """Association table between Cards and Decks"""
    __tablename__ = "card_decks"

    card_deck_id = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True)
    card_id = db.Column(db.Integer, db.ForeignKey("cards.card_id"))
    deck_id = db.Column(db.Integer, db.ForeignKey("decks.deck_id"))

    def __repr__(self):
        return f"<CardDeck card_deck_id={self.card_deck_id}, card_id={self.card_id}, deck_id={self.deck_id}>"
    
    @classmethod
    def add_card(cls, card_id, deck_id):
        return cls(card_id=card_id, deck_id=deck_id)
    
    @classmethod
    def get_by_deck_id(cls, deck_id):
        return db.session.query(cls).filter_by(deck_id = deck_id).all()
    
    @classmethod
    def get_by_card_id(cls, card_id):
        return cls(card_id=card_id)
    
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