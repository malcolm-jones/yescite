import os

def lines_bib_to_keep(lines_bbl,lines_bib):
    lines_bbl = [line for line in lines_bbl if "\\entry{" in line]
    cited_aliases = [line.split("entry{")[1].split("}")[0] for line in lines_bbl]

    lines_bib_to_keep = []
    for i in range(len(lines_bib)):
        line = lines_bib[i]
        if "@" in line:
            alias = line.split("{")[1].split(",")[0]
            if alias in cited_aliases:
                j = i
                not_found_end = True
                while not_found_end:
                    j += 1
                    if lines_bib[j].replace(" ","") in ["}\n","}"]:
                        not_found_end = False
                lines_bib_to_keep.append(lines_bib[i:j+1])
    new_bib = [line for item in lines_bib_to_keep for line in item]

    return new_bib

def yescite(
        app=False,
        path_bbl="example/example.bbl",
        path_bib="example/example.bib",
        path_yescite="output/yescite.bib",
        lines_bbl=None,
        lines_bib=None,
):
    if not app:
        with open(path_bbl,"r",encoding='utf-8') as f:
            lines_bbl = f.readlines()
        with open(path_bib,"r",encoding='utf-8') as f:
            lines_bib = f.readlines()
        new_bib = lines_bib_to_keep(lines_bbl,lines_bib)

        if not os.path.exists("output/"):
            os.makedirs("output/")

        with open(path_yescite, 'w', encoding='utf-8') as file:
            for line in new_bib:
                file.write(line)
        return None
    else:        
        return lines_bib_to_keep(lines_bbl,lines_bib)
