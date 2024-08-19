import json
import csv
# added this line to test git
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
                # print(f"Processing row: Ambiguity = {row[0]}")  # Debug print
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
        name = card['name'].lower()
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
                'discrepancy': 'Name not found in db'
            })
        else:
            # Check if there's an exact match (name, artist, and set)
            exact_match = any(c for c in name_matches if c['artist'] == artist and c['set'].lower() == set_code.lower())
            
            if not exact_match:
                # Find the discrepancies
                artist_mismatch = not any(c for c in name_matches if c['artist'] == artist)
                set_mismatch = not any(c for c in name_matches if c['set'].lower() == set_code.lower())
                
                if artist_mismatch and set_mismatch:
                    discrepancy = 'Artist and set not found in db'
                elif artist_mismatch:
                    discrepancy = 'Artist not found in db'
                else:
                    discrepancy = 'Set not found in db'

                # Find the correct combinations in the database
                correct_artists = set(c['artist'] for c in name_matches)
                correct_sets = set(c['set'].lower() for c in name_matches)

                discrepancies.append({
                    'ambiguity': ambiguity,
                    'name': card['name'],
                    'set_code': set_code,
                    'artist': artist,
                    'discrepancy': discrepancy,
                    'correct_artists': ', '.join(correct_artists),
                    'correct_sets': ', '.join(correct_sets)
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
with open('discrepancies.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['ambiguity', 'name', 'set_code', 'artist', 'discrepancy', 'correct_artists', 'correct_sets']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for discrepancy in discrepancies:
        writer.writerow(discrepancy)

print("Discrepancies written to 'discrepancies.csv'")