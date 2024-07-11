import json


with open('./source/default-cards-20240702090634.json','r', encoding='utf-8') as file:
    data = json.load(file)
# Open original JSON file, and set which fields that will be pulled from the file"
desired_fields = ['name', 'mana_cost', 'cmc', 'type_line', 'oracle_text']
processed_data = []
processed_ids = set()

for card in data:
    card_id = card.get('id')
    if card_id in processed_ids:
        continue

    processed_ids.add(card_id)
    new_card = {}

# Applies to cards that have 2 faces. Front and back faces for a single card.
    if 'card_faces' in card:
        for i, face in enumerate(card['card_faces']):
            suffix = '_front' if i == 0 else '_back'
            for field in desired_fields:
                new_card[f'{field}{suffix}'] = face.get(field, None)

            if 'image_uris' in face:
                new_card[f'img_uri_small{suffix}'] = face['image_uris'].get('small')
                new_card[f'img_uri_normal{suffix}'] = face['image_uris'].get('normal')
            else:
                new_card[f'img_uri_small{suffix}'] = None
                new_card[f'img_uri_normal{suffix}'] = None
    else:
        suffix = '_front'
        for field in desired_fields:
            new_card[f'{field}{suffix}'] = card.get(field, None)

        if 'image_uris' in card:
            new_card[f'img_uri_small{suffix}'] = card['image_uris'].get('small')
            new_card[f'img_uri_normal{suffix}'] = card['image_uris'].get('normal')
        else:
            new_card['img_uri_small'] = None
            new_card['img_uri_normal'] = None

    processed_data.append(new_card)

with open('./source/MTG_Cards.json', 'w', encoding='utf-8') as output_file:
    json.dump(processed_data, output_file, ensure_ascii=False, indent=4)
