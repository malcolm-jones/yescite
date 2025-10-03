import os
from dotenv import load_dotenv

load_dotenv()

def utf8len(s):
    return len(s.encode('utf-8'))

def some_line_starts_with(lines, symbol):
    return sum([x.lstrip().startswith(symbol) for x in lines]) > 0

# Validation for each input

def valid_bbl(input_bbl):
    lines_bbl = input_bbl.splitlines()
    return (
        utf8len(input_bbl) < int(os.getenv("INPUT_LIMIT"))
        and some_line_starts_with(lines_bbl, "\entry")
    )

def valid_bib(input_bib):
    lines_bib = input_bib.splitlines()
    return (
        utf8len(input_bib) < int(os.getenv("INPUT_LIMIT"))
        and some_line_starts_with(lines_bib, "@")
    )

# Validation for each endpoint

def valid_yescite(input_bbl, input_bib):
    return (
        valid_bbl(input_bbl)
        and valid_bib(input_bib)
    )

def valid_bibtocsv(input_bib):
    return (
        valid_bib(input_bib)
    )

def valid_bibformat(input_bib):
    return (
        valid_bib(input_bib)
    )

def valid_arxivversions(input_bib):
    return (
        valid_bib(input_bib)
    )

### DEVELOPMENT

# from yescite import paths_to_lines
# lines_bbl, lines_bib = paths_to_lines(
#     os.getenv("PATH_EXAMPLE_BBL"),
#     os.getenv("PATH_EXAMPLE_BIB"),
# )
