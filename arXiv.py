import feedparser
import urllib.parse
import re

def query_title(title):

    # Longest sequence of complete words in title without special characters
    l = title.split(" ")
    segments = []
    new_segment = []
    for n in range(len(l)):
        if len(re.split('[^a-zA-Z]', l[n])) == 1:
            new_segment.append(l[n])
        else:
            segments.append(new_segment)
            new_segment = []
    segments.append(new_segment)
    segments = [" ".join(segment) for segment in segments]
    max_segment = max(segments, key=len)

    # Query arXiv API
    clue = urllib.parse.quote(f'"{max_segment}"')
    url = ''.join([
        "http://export.arxiv.org/api/query?",
        f"search_query=ti:{clue}&sortBy=lastUpdatedDate&sortOrder=ascending",
    ])
    d = feedparser.parse(url)
    print(f"Title matched with {len(d.entries)} entries.")

    return d

# ## Development
# title = "Ideals of {S}teinberg algebras of strongly effective groupoids, with applications to {L}eavitt path algebras"
# d
# d.feed.title
# for n in range(len(d.entries)):
#     print(d.entries[n].title)
