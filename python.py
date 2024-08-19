import json
import csv

# Load the Scryfall card data from JSON file
with open('oracle-cards.json', 'r') as file:
    scryfall_cards = json.load(file)
    # Convert card names to lowercase for case-insensitive matching
    scryfall_cards = [{**card, 'name': card['name'].lower()} for card in scryfall_cards]

def load_tsv_data(tsv_file):
    try:
        with open(tsv_file, 'r') as file:
            reader = csv.reader(file, delimiter='\t')
            header = next(reader)  # Get the header row

            cards = []
            for row in reader:
                print(f"Processing row: Ambiguity = {row[0]}")  # Debug print
                cards.append({
                    'ambiguity': row[0],
                    'name': row[4],  # Updated column index for name
                    'set_code': row[9],
                    'artist': row[10]
                })
        return cards, header
    except Exception as e:
        print(f"Error reading TSV file: {e}")
        return [], []

def check_cards(cards, scryfall_cards, header):
    discrepancies = []
    total_cards = len(cards)
    for i, card in enumerate(cards, start=1):
        name = card['name'].lower()  # Convert name to lowercase
        artist = card['artist']
        set_code = card['set_code']
        ambiguity = card['ambiguity']

        # Search for cards with the same name in the Scryfall data
        name_matches = [c for c in scryfall_cards if c['name'] == name]

        if not name_matches:
            # Name doesn't match any card in the database
            discrepancies.append({
                'ambiguity': ambiguity,
                'name': card['name'],
                'set_code': set_code,
                'artist': artist,
                'discrepancy': 'Name mismatch'
            })
        else:
            # Name matches at least one card in the database
            matching_cards = [c for c in name_matches if c['artist'] == artist and c['set'].lower() == set_code.lower()]
            if not matching_cards:
                # Artist and/or set code don't match any card with the same name
                artist_mismatch = False
                set_mismatch = False
                for c in name_matches:
                    if c['artist'] != artist:
                        artist_mismatch = True
                    if c['set'].lower() != set_code.lower():
                        set_mismatch = True

                if artist_mismatch and set_mismatch:
                    discrepancy = 'Artist and set mismatch'
                elif artist_mismatch:
                    discrepancy = 'Artist mismatch'
                else:
                    discrepancy = 'Set mismatch'

                discrepancies.append({
                    'ambiguity': ambiguity,
                    'name': card['name'],
                    'set_code': set_code,
                    'artist': artist,
                    'discrepancy': discrepancy
                })

        # Print progress every 100 cards
        if i % 100 == 0:
            print(f"Processed {i}/{total_cards} cards")

    return discrepancies

cards, header = load_tsv_data('cards.tsv')
discrepancies = check_cards(cards, scryfall_cards, header)
num_mismatches = len(discrepancies)

print(f"Number of mismatches found: {num_mismatches}")

# Write discrepancies to a CSV file
with open('discrepancies.csv', 'w', newline='') as csvfile:
    fieldnames = ['ambiguity', 'name', 'set_code', 'artist', 'discrepancy']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for discrepancy in discrepancies:
        writer.writerow(discrepancy)

print("Discrepancies written to 'discrepancies.csv'")