import os
import sys
import time

from utils import *

args = " ".join(sys.argv[1:])
_, search_words = normalize_text(args)
search_words = [word for word in search_words if word not in ["PUNCT", "STOPWORD", "NUM"]]

start = time.time()
for subdir, dirs, files in os.walk("../sites/"):
    for file in files:
        if file.endswith(".html"):
            filename = os.path.join(subdir, file)
            tokenized_text, normalized_text = normalize_text(open(filename, 'r').read())

            index = 0
            for word in normalized_text:
                if word in search_words:
                    print("Found word: " + word + " - at index " + str(index) + " in file: " + filename)
                index += 1

print("Search took: " + str(time.time() - start) + " seconds")
