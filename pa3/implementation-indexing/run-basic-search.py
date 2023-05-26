import os
import sys
import time

from utils import *

args = " ".join(sys.argv[1:])
_, search_words = normalize_text(args)
search_words = [word for word in search_words if word not in ["PUNCT", "STOPWORD", "NUM"]]
def get_snippets(filename, indexes):
    radious = 3
    snippets = []
    html_file = open(filename, 'r',encoding='utf-8').read()
    html = tokenize_html_text(html_file)
    #select if in not in range 
    new_indexes = [indexes[0]]
    for i in range(1,len(indexes)):
        if indexes[i] - indexes[i-1] > radious:
            new_indexes.append(indexes[i])
    for index in new_indexes:
        new_snippet = []
        old = ""
        for i, word in enumerate(html[max(0, index-radious):min(index + radious, len(html))]):
            word = old + word
            old = ""
            if word in ".!?,:;)]}":
                if len(new_snippet)>0:
                    new_snippet[-1] = new_snippet[-1] + word
            elif word in "([{":
                if i <5:
                    old = word
                else:
                    new_snippet.append(word)
            else:
                new_snippet.append(word)
        snippets.append(" ".join(new_snippet))        
    return snippets

start = time.time()
results = []
for subdir, dirs, files in os.walk("../sites/"):
    for file in files:
        if file.endswith(".html"):
            frequency = 0
            indexes = []

            filename = os.path.join(subdir, file)
            tokenized_text, normalized_text = normalize_text(open(filename, 'r').read())

            index = 0
            for word in normalized_text:
                if word in search_words:
                    frequency += 1
                    indexes.append(index)
                    #print("Found word: " + word + " - at index " + str(index) + " in file: " + filename)
                index += 1
        if frequency > 0:
            results.append([os.path.join(subdir, file), frequency, indexes])

print("Search took: " + str(time.time() - start) + " seconds")
print("Frequencies Document                                  Snippet")
print("----------- ----------------------------------------- -----------------------------------------------------------")
for result in sorted(results,key=lambda x: x[1],reverse=True):
    site = result[0]
    frequency = result[1]
    indexes = result[2]
    snippet = " ... ".join(get_snippets(site, indexes))
    print(str(frequency) + "           " + "/".join(site.split("/")[2:]) + "           " + snippet + "\n")
