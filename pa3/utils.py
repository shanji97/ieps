import re

from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from string import punctuation

def truncate_table(cursor, conn):
    cursor.execute("DELETE FROM IndexWord")
    cursor.execute("DELETE FROM Posting")
    conn.commit()

def insert_into_word_index(cursor, conn, word):
    res = cursor.execute('SELECT * FROM IndexWord WHERE word=?;', (word,))

    if res.fetchone() is None:
        cursor.execute('INSERT INTO IndexWord VALUES (?);', (word,))
        conn.commit()

def insert_into_posting(cursor, conn, word, document_name, frequency, indexes):
    insert_into_word_index(cursor, conn, word)
    indexes_string = ",".join([str(x) for x in indexes])
    cursor.execute('INSERT INTO Posting VALUES (?, ?, ?, ?);',
                   (word, document_name, frequency, indexes_string))
    conn.commit()

def insert_into_db_many(cursor, conn, insert_dict):
    cursor.executemany('INSERT INTO IndexWord VALUES (?);', list(set([(item[0], ) for item in insert_dict.keys()])))
    cursor.executemany('INSERT INTO Posting VALUES (?, ?, ?, ?);', insert_dict.values())
    conn.commit()

def get_html_text(html_file):
    # nltk.download('punkt')
    soup = BeautifulSoup(html_file, features="html.parser")
    text = soup.get_text()
    text = re.sub(re.compile('<.*?>'), '', text)

    # TODO remove punctuation
    # TODO remove stopwords (with nltk, spacy, ...)
    # TODO remove numbers
    # TODO lemmatize (with classla, nltk, spacy, ...)

    text = '\n'.join([line.strip() for line in text.splitlines() if line.strip()])
    tokenized_text = word_tokenize(text, language='slovene')
    tokenized_text_lower = [word.lower() for word in tokenized_text]
    normalized_text = [word if word not in punctuation else "PUNCT" for word in tokenized_text_lower]
    return tokenized_text, normalized_text
