import os
import sqlite3
import time
import utils

if __name__ == "__main__":
    conn = sqlite3.connect('inverted-index.db')
    cursor = conn.cursor()
    utils.truncate_table(cursor, conn)

    start_time = time.time()

    insert_dict = {}
    words_set = ()
    for subdir, dirs, files in os.walk("../sites/"):
        for file in files:
            if file.endswith(".html"):
                filename = os.path.join(subdir, file)
                print("Inserting from file: " + filename)
                html_file = open(filename, 'r',encoding='utf-8').read()
                _, normalized_text = utils.normalize_text(html_file)

                text_occurance_count = {}
                for index, word in enumerate(normalized_text):
                    if word not in ["PUNCT", "STOPWORD", "NUM"]:
                        if word not in text_occurance_count:
                            text_occurance_count[word] = {}
                            text_occurance_count[word]["count"] = 1
                            text_occurance_count[word]["indexes"] = [index]
                        else:
                            text_occurance_count[word]["count"] += 1
                            text_occurance_count[word]["indexes"].append(index)

                for word in text_occurance_count:
                    indexes_string = ",".join([str(x) for x in text_occurance_count[word]["indexes"]])
                    words_set = words_set + (word,)
                    insert_dict[(word, filename)] = (
                        word,
                        filename,
                        text_occurance_count[word]["count"],
                        indexes_string
                    )

        utils.insert_into_db_many(cursor, conn, insert_dict)

    print("Inserted in: " + str(time.time() - start_time) + " seconds")
