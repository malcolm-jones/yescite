import os
from dotenv import load_dotenv

load_dotenv()

def utf8len(s):
    return len(s.encode('utf-8'))

def valid_yescite(input_bbl, input_bib_YesCite):
    return (
        utf8len(input_bbl) < int(os.getenv("INPUT_LIMIT"))
        and utf8len(input_bib_YesCite) < int(os.getenv("INPUT_LIMIT"))
    )

def valid_bibtocsv(input_bib_to_csv):
    return (
        utf8len(input_bib_to_csv) < int(os.getenv("INPUT_LIMIT"))
    )
