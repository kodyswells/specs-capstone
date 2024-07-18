import os
import json
from model import User, Card, Deck, CardDeck, Library, connect_to_db
from random import randint, choice
from server import app
import model

"""Script to seed the database"""


os.system('dropdb MTG')
os.system('createdb MTG --encoding=UTF8')

model.connect_to_db(app)
with app.app_context():
    model.db.create_all()

    """Load MTG card info from the JSON"""
    with open('source/MTG_Cards.json', encoding='utf-8') as f:
        card_data = json.loads(f.read())

    cards_in_db = []
    for card in card_data:
        name_front = card.get("name_front", "")
        cmc_front = card.get("cmc_front", 0) if card.get("cmc_front") is not None else 0
        type_line_front = card.get("type_line_front", "")
        oracle_text_front = card.get("oracle_text_front", "")
        img_uri_small_front = card.get("img_uri_small_front", "") if card.get("img_uri_small_front") is not None else ""
        img_uri_normal_front = card.get("img_uri_normal_front", "") if card.get("img_uri_normal_front") is not None else ""
        name_back = card.get("name_back", "")
        cmc_back = card.get("cmc_back", 0) if card.get("cmc_back") is not None else 0
        type_line_back = card.get("type_line_back", "")
        oracle_text_back = card.get("oracle_text_back", "")
        img_uri_small_back = card.get("img_uri_small_back", "") if card.get("img_uri_small_back") is not None else ""
        img_uri_normal_back = card.get("img_uri_normal_back", "") if card.get("img_uri_normal_back") is not None else ""

        # print(f"Processing card: {name_front}")
        # print(f"cmc_front: {cmc_front}")
        # print(f"type_line_front: {type_line_front}")
        # print(f"oracle_text_front: {oracle_text_front}")
        # print(f"img_uri_small_front: {img_uri_small_front}")
        # print(f"img_uri_normal_front: {img_uri_normal_front}")
        # print(f"name_back: {name_back}")
        # print(f"cmc_back: {cmc_back}")
        # print(f"type_line_back: {type_line_back}")
        # print(f"oracle_text_back: {oracle_text_back}")
        # print(f"img_uri_small_back: {img_uri_small_back}")
        # print(f"img_uri_normal_back: {img_uri_normal_back}")

        db_card = Card(
            name_front=name_front,
            cmc_front=cmc_front,
            type_line_front=type_line_front,
            oracle_text_front=oracle_text_front,
            img_uri_small_front=img_uri_small_front,
            img_uri_normal_front=img_uri_normal_front,
            name_back=name_back,
            cmc_back=cmc_back,
            type_line_back=type_line_back,
            oracle_text_back=oracle_text_back,
            img_uri_small_back=img_uri_small_back,
            img_uri_normal_back=img_uri_normal_back
        )
        cards_in_db.append(db_card)
    
    model.db.session.add_all(cards_in_db)  
    model.db.session.commit()
