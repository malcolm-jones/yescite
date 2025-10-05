import os
from itertools import groupby
import pandas as pd
from tqdm import tqdm
import feedparser
import urllib.parse
import re

def paths_to_lines(bbl_path, bib_path):
    with open(bbl_path, 'r', encoding='utf-8') as f:
        bbl_lines = f.readlines()
    with open(bib_path, 'r', encoding='utf-8') as f:
        bib_lines = f.readlines()
    return bbl_lines, bib_lines

class YesCite:
    """Features lines from .bib and .bbl and the associated yescite.

        Attributes:
            bbl (list) -- Lines in a .bbl
            bib (list) -- Lines in a .bib
            aliases_used (list) -- The aliases occuring in bbl
            aliases_all (list) -- The aliases occuring in bib
            aliases_unused (list) -- The aliases in bib but not bbl
            yescite (list) -- Sublist of bib giving the entries in bbl
    """
    def __init__(self, bbl_lines, bib_lines):
        self.bbl = bbl_lines
        self.bib = bib_lines

        lines_wth_aliases = [
            line for line in self.bbl if '\\entry{' in line
        ]
        self.aliases_used = [
            line.split('entry{')[1].split('}')[0] for line in lines_wth_aliases
        ]
        
        self.aliases_all = [
            line.split('{')[1].split(',')[0] for line in self.bib if '@' in line
        ]
        
        self.aliases_unused = [
            alias for alias in self.aliases_all if alias not in self.aliases_used
        ]
        
        yescite = []
        for i in range(len(self.bib)):
            line = self.bib[i]
            if '@' in line:
                alias = line.split('{')[1].split(',')[0]
                if alias in self.aliases_used:
                    j = i
                    not_found_end = True
                    while not_found_end:
                        j += 1
                        if self.bib[j].replace(' ', '') in ['}\n', '}']:
                            not_found_end = False
                    yescite.append(self.bib[i:j+1] + ['\n'])
        self.yescite = [
            line for item in yescite for line in item
        ]

def bib_to_df(lines_bib):
    """Convert the a .bib file to a DataFrame.

        Parameters:
            lines_bib (list of strings) -- The lines of a .bib file

        Returns:
            df (pd.DataFrame) -- A pandas DataFrame containing the entries in 
            the .bib.
    """    
    # left-align (remove left-side spaces)
    lines_bib = [x.lstrip() for x in lines_bib]
    # remove empty lines
    lines_bib = [x for x in lines_bib if len(x) != 0] 
    # remove comments
    lines_bib = [x for x in lines_bib if x[0] != "%"]
    # remove ending commas
    lines_bib = [x[:-1] if x[-2:] in ["},","\","] else x for x in lines_bib]
    # make sure closing brackets of all entries are on their own line 
    new_entry_indices = [n for n in range(len(lines_bib)) 
                         if lines_bib[n].startswith("@")]
    assert new_entry_indices[0] == 0
    new_entry_indices.reverse()
    for i in new_entry_indices[:-1]:
        if not lines_bib[i-1].startswith("}"):
            lines_bib[i-1] = lines_bib[i-1][:-1]
            lines_bib.insert(i, "}")

    # remove leading and trailing whitespace
    lines_bib = [x.strip() for x in lines_bib]

    # add entry type and reformat label like it's a field
    new = []
    for n in range(len(lines_bib)):
        line = lines_bib[n]
        if line[0] == "@":
            # add lines corresponding to type of reference (e.g. article)
            reftype = line.split("@")[1].split("{")[0].replace(' ', '')
            new.append("type = {" + reftype + "}")
            # reformat citation label
            label = line.split("{")[1][:-1].strip()
            new.append("label = {" + label + "}")
        else:
            new.append(line)
    lines_bib = new

    # collapse field entries where bookends are on separate lines
    reading = True
    n = 0
    while reading:
        line = lines_bib[n]
        if line.endswith("{"):
            lines_bib[n] = line + lines_bib[n+1]
            del lines_bib[n+1]
        n += 1
        reading = n in range(len(lines_bib))
    reading = True
    n = 0
    while reading:
        if (
            lines_bib[n] == "}"
            and n + 1 in range(len(lines_bib)) 
            and not lines_bib[n+1].startswith("type = {")
        ):
            lines_bib[n-1] = lines_bib[n-1] + lines_bib[n]
            del lines_bib[n]
        else:
            n += 1
        reading = n in range(len(lines_bib))
    
    # separate into lists of lists
    items = [
        list(group) 
        for k, group in groupby(lines_bib, key=lambda x: x == "}") if not k
    ]

    # join together any features of the entry occupying multiple lines
    for m in range(len(items)):
        item = items[m]
        n = 0
        while n < len(item):
            x = item[n]
            x = "".join(c for c in x if not c.isalpha()).lstrip()
            if x.startswith("="):
                n += 1
            else:
                item[n-1] = ' '.join([item[n-1], item[n]])
                item.pop(n)

    # make into dictionary and convert to DataFrame
    for m in range(len(items)):
        for n in range(len(items[m])):
            x = items[m][n].split("=", 1)
            y = x[0].lstrip().rstrip().lower()
            data = x[1].lstrip().rstrip()
            if data.startswith("{") and data.endswith("}"):
                data = data[1:-1]
            elif data.startswith("\"") and data.endswith("\""):
                data = data[1:-1]
            items[m][n] = [y, data]
    dicts = [dict(entry) for entry in items]
    df = pd.DataFrame(dicts)

    return df

def extract_entry(df, n):
    formatting = {
        "space_after_entry_type": True,
        "spaces_surrounding_equals": True,
        "lower_or_upper": "lower",
        "align": "equals",
        "bookends": "braces",
    }
    entry_type = df.iloc[n]["type"]
    entry_label = df.iloc[n]["label"]
    fields = list(df.columns)
    fields.remove("type")
    fields.remove("label")
    s = df.iloc[n][fields]
    if formatting["lower_or_upper"] == "upper":
        entry_type = entry_type.upper()
        fields = [x.upper() for x in fields]
    elif formatting["lower_or_upper"] == "lower":
        entry_type = entry_type.lower()
        fields = [x.lower() for x in fields]
    if formatting["align"] == "tab":
        padding = [4]*len(fields)
    elif formatting["align"] == "left":
        padding = [0]*len(fields)
    elif formatting["align"] == "equals":
        max_field_length = max([len(x) for x in fields])
        padding = [max_field_length - len(x) for x in fields]
    padding_dict = dict(zip(fields, padding))
    if formatting["bookends"] == "quotes":
        bookend_left = "\""
        bookend_right = "\""
    elif formatting["bookends"] == "braces":
        bookend_left = "{"
        bookend_right = "}"
    l = []
    for i in range(len(s)):
        if str(s.values[i]) != "nan":
            x = ''.join([
                padding_dict[fields[i]]*" ",
                fields[i],
                int(formatting["spaces_surrounding_equals"])*" ",
                "=",
                int(formatting["spaces_surrounding_equals"])*" ",
                bookend_left,
                str(s.values[i]),
                bookend_right,
            ])
            l.append(x)
    entry = ''.join([
        "@",entry_type,
        int(formatting["space_after_entry_type"])*" ",
        "{",
        entry_label,
        ",\n",
        ",\n".join(l),
        "\n}",
    ])
    return entry

def extract_entries(df):
    N = df.shape[0]
    entries = [extract_entry(df, n) for n in range(N)]
    return "\n\n".join(entries)

def add_arXiv_versions(df):

    arXivresults = []
    for title in tqdm(df.title):
        d, search_term = query_title(title)
        arXivsearchterm = search_term
        arXivmatches = len(d.entries)
        if arXivmatches == 1:
            arXivversionurl = d.entries[0].id
        else:
            arXivversionurl = None
        arXivresults.append({
            "arXivsearchterm": arXivsearchterm,
            "arXivmatches": arXivmatches,
            "arXivversionurl": arXivversionurl,
        })

    df["arXivsearchterm"] = [x["arXivsearchterm"] for x in arXivresults]
    df["arXivmatches"] = [x["arXivmatches"] for x in arXivresults]
    df["arXivversionurl"] = [x["arXivversionurl"] for x in arXivresults]

    num_unique_matches = sum([x==1 for x in df["arXivmatches"]])

    return df, num_unique_matches

def path_to_df(path_bib="example/example.bib"):
    with open(path_bib, 'r', encoding='utf-8') as f:
        lines_bib = f.readlines()
    lines_bib = [x.removesuffix("\n") for x in lines_bib]
    x = lines_bib[5]
    df = bib_to_df(lines_bib)
    return df

def query_title(title):

    # New strategy
    replacements = [
        ["\c{c}", "ç"],
        ["{\c{c}}", "ç"],
        ["\'e", "é"],
        ["{\'e}", "é"],
        ["’", "'"],
        ["–", " "], # API does not like hyphens
        ["-", " "], # API does not like hyphens
        ["‐", " "], # API does not like hyphens
    ]
    for replacement in replacements:
        title = title.replace(replacement[0], replacement[1])
    l = title.split(" ")
    regex = re.compile('[^0-9a-zA-Zà-üÀ-Ü/-]')
    l = [regex.sub('', x) for x in l]
    search_term = " ".join(l)

    # # Groom title
    # replacements = [
    #     ["\c{c}", "ç"],
    #     ["{\c{c}}", "ç"],
    #     ["\'e", "é"],
    #     ["{\'e}", "é"],
    #     ["’", "'"],
    #     ["{", ""],
    #     ["}", ""],
    # ]
    # for replacement in replacements:
    #     title = title.replace(replacement[0], replacement[1])
    # # Longest sequence of complete words in title without special characters
    # l = title.split(" ")
    # for n in range(len(l)):
    #     if l[n].endswith(".") or l[n].endswith(",") or l[n].endswith(":"):
    #         l[n] = l[n][:-1]
    # segments = []
    # new_segment = []
    # for n in range(len(l)):
    #     if len(re.split('[^a-zA-Zà-üÀ-Ü-–]', l[n])) == 1:
    #         new_segment.append(l[n])
    #     else:
    #         segments.append(new_segment)
    #         new_segment = []
    # segments.append(new_segment)
    # segments = [" ".join(segment) for segment in segments]
    # max_segment = max(segments, key=len)
    # max_segment = max_segment.replace("-", " ")
    # max_segment = max_segment.replace("–", " ")
    # search_term = max_segment

    # Query arXiv API
    clue = urllib.parse.quote(f'"{search_term}"')
    url = f"http://export.arxiv.org/api/query?search_query=ti:{clue}"
    d = feedparser.parse(url)

    return d, search_term


# ## Development
# df = path_to_df()
# with open("test.txt", 'a') as file:
#     file.writelines(extract_entries(df))
#     file.writelines("\n")


# d
# d.feed.title
# for n in range(len(d.entries)):
#     print(d.entries[n].title)
