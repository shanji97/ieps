import os
import sqlite3
import sys
import time
import utils

html_files_dir = "../sites/"
db_filename = sys.argv[1]
files_num = sum([len(files) for r, d, files in os.walk(html_files_dir)])
files_inserted = 0
if __name__ == "__main__":
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    try:
        utils.create_tables(cursor, conn)
    except Exception:
        pass
    utils.truncate_table(cursor, conn)

    start_time = time.time()

    insert_dict = {}
    words_set = ()
    insert_dict_all = {}
    for subdir, dirs, files in os.walk(html_files_dir):
        files = sorted(files)
        for file in files:
            if file.endswith(".html"):
                filename = os.path.join(subdir, file)
                print("Inserting file " + str(files_inserted) + "/" + str(files_num) + " - " + filename)
                html_file = open(filename, 'r', encoding='utf-8').read()
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

                files_inserted += 1

        insert_dict_all.update(insert_dict)
    utils.insert_into_db_many(cursor, conn, insert_dict)

    print("Inserted in: " + str(time.time() - start_time) + " seconds")
