import os
from itertools import groupby
import pandas as pd

def lines_bib_to_keep(
        lines_bbl, 
        lines_bib,
):
    """Find the entries in lines_bib mentioned in lines_bbl.

        Parameters:
            lines_bbl (list) -- The lines of a .bbl file
            lines_bib (list) -- The lines of a .bib file

        Returns:
            new_bib (list) -- The sublist of lines_bib containing all the 
                lines for those entries in .bib that are mentioned in .bbl
    """
    lines_bbl = [
        line for line in lines_bbl if '\\entry{' in line
    ]
    cited_aliases = [
        line.split('entry{')[1].split('}')[0] for line in lines_bbl
    ]

    lines_bib_to_keep = []
    for i in range(len(lines_bib)):
        line = lines_bib[i]
        if '@' in line:
            alias = line.split('{')[1].split(',')[0]
            if alias in cited_aliases:
                j = i
                not_found_end = True
                while not_found_end:
                    j += 1
                    if lines_bib[j].replace(' ', '') in ['}\n', '}']:
                        not_found_end = False
                lines_bib_to_keep.append(lines_bib[i:j+1])
    new_bib = [
        line for item in lines_bib_to_keep for line in item
    ]

    return new_bib

def yescite(
        path_bbl='example/example.bbl',
        path_bib='example/example.bib',
        path_yescite='output/yescite.bib',
):
    """Wrapper for lines_bib_to_keep for local use.

        Keyword arguments:
            path_bbl (str) -- Path for .bbl (default 'example/example.bbl')
            path_bib (str) -- Path for .bib (default 'example/example.bib')
            path_yescite (str) -- Path for output (default 'output/yescite.bib')
        
        Returns:
            Nothing but new_bib is written to the path path_yescite.
    """
    with open(path_bbl, 'r', encoding='utf-8') as f:
        lines_bbl = f.readlines()
    with open(path_bib, 'r', encoding='utf-8') as f:
        lines_bib = f.readlines()
    new_bib = lines_bib_to_keep(lines_bbl, lines_bib)

    if not os.path.exists('output/'):
        os.makedirs('output/')

    with open(path_yescite, 'w', encoding='utf-8') as file:
        for line in new_bib:
            file.write(line)
    return None

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
    new = []
    for n in range(len(lines_bib)):
        line = lines_bib[n]
        if line[0] == "@":
            # add lines corresponding to type of reference (e.g. article)
            reftype = line.split("@")[1].split("{")[0].replace(' ', '')
            new.append("type = {" + reftype + "}")
            # reformat citation label
            label = line.split("{")[1][:-1]
            new.append("label = {" + label + "}")
        else:
            new.append(line)
    lines_bib = new

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
            items[m][n] = [y, data[1:-1]]
    dicts = [dict(entry) for entry in items]
    df = pd.DataFrame(dicts)

    return df

### Development
# with open(path_bib, 'r', encoding='utf-8') as f:
#     lines_bib = f.readlines()
# lines_bib = [x.removesuffix("\n") for x in lines_bib]
# x = lines_bib[5]
