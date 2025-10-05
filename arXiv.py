import feedparser
import urllib.parse
import re

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

# ## Development
# title = "Ideals of {S}teinberg algebras of strongly effective groupoids, with applications to {L}eavitt path algebras"
# d
# d.feed.title
# for n in range(len(d.entries)):
#     print(d.entries[n].title)
    return d, search_term
