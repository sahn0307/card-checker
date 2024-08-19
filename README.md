# Card Checker
## Installation
Clone repo down to your local machine

Install dependencies (recommend using a virtual environment) $pipenv install

## Usage
Add json database and .tsv file for comparison to project folder

By default, tsv should be named cards.tsv and scryfall database should be named oracle-cards.json

Columns in .tsv are processed by default as the following:

0: Ambiguity

4: Name

9: Set Code

10: Artist

These can be edited in the python.py file in rows 20-23

Run the python file with $python python.py

This will create a csv file in your project directory called discrepancies.tsv
