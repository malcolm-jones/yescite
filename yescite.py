import os

def lines_bib_to_keep(
        lines_bbl, 
        lines_bib
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
        use_app=False,
        path_bbl='example/example.bbl',
        path_bib='example/example.bib',
        path_yescite='output/yescite.bib',
        lines_bbl=None,
        lines_bib=None,
):
    """Wrapper for lines_bib_to_keep to switch between web app and local use.

        Keyword arguments:
            use_app -- True if used by the web app and False if the function is 
                to be run locally for saved .bib and .bbl files (default False)
            path_bbl (str) -- Path for .bbl (default 'example/example.bbl')
            path_bib (str) -- Path for .bib (default 'example/example.bib')
            path_yescite (str) -- Path for output (default 'output/yescite.bib')
            lines_bbl (list) -- The lines of a .bbl file (default None)
            lines_bib (list) -- The lines of a .bib file (default None)
        
        Returns:
            If not use_app, nothing is returned by the new_bib returned by
                lines_bib_to_keep is written to the path path_yescite.
            If use_app, returns lines_bib_to_keep, which the web app will put
                in a textarea for the user.
    """
    if not use_app:
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
    else:        
        return lines_bib_to_keep(lines_bbl, lines_bib)
