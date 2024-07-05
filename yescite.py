import os

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
