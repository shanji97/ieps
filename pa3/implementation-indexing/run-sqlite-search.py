from utils import *
import sqlite3
import time
import sys

conn = sqlite3.connect('inverted-index.db')
cursor = conn.cursor()
#_, search_words = normalize_text(" ".join(["Sistem", "SPOT"]))

def get_snippets(filename, indexes):
    radious = 3
    snippets = []
    html_file = open(filename, 'r',encoding='utf-8').read()
    html = tokenize_html_text(html_file)
    for index in indexes:
        snippets.append(" ".join(html[max(0, index-radious):min(index + radious, len(html))]))
    return snippets

args = " ".join(sys.argv[1:])
_, search_words = normalize_text(args)
search_words = [word for word in search_words if word not in ["PUNCT", "STOPWORD", "NUM"]]

start = time.time()
queries = []
for i, word in enumerate(search_words):
    queries.append("SELECT documentName, frequency, indexes FROM Posting WHERE word = '"+  word +"'")
query = " UNION ALL ".join(queries)
#query = "SELECT * FROM (" + query + ") WHERE documentName IN (SELECT documentName FROM (" + query + ") GROUP BY documentName HAVING count(*) >= 2)"

#Only if all words are present
query = "SELECT documentName, sum(frequency), group_concat(indexes) FROM (" + query + ") GROUP BY documentName HAVING count(*) >= 2 ORDER BY sum(frequency) DESC"
#ALLow missing words
#query = "SELECT documentName, sum(frequency), group_concat(indexes) FROM (" + query + ") GROUP BY documentName ORDER BY sum(frequency) DESC"


print(query)
res = cursor.execute(query)
print("Search took: " + str(time.time() - start) + " seconds")
print("Frequencies Document                                  Snippet")
print("----------- ----------------------------------------- -----------------------------------------------------------")
for result in res.fetchall():
    site = result[0]
    frequency = result[1]
    indexes = sorted([int(x) for x in result[2].split(",")])
    snippet = "...".join(get_snippets(site, indexes))
    print(str(frequency) + "           " + "/".join(site.split("/")[2:]) + "           " + snippet + "\n")
