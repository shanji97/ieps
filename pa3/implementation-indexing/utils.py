import re
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords as sw
import nltk
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
    cursor.executemany('INSERT INTO IndexWord VALUES (?);', list(
        set([(item[0], ) for item in insert_dict.keys()])))
    cursor.executemany(
        'INSERT INTO Posting VALUES (?, ?, ?, ?);', insert_dict.values())
    conn.commit()


def get_html_text(html_file):
    # NLTK downloads
    # nltk.download('punkt')
    # nltk.download('stopwords')
    # nltk.download('wordnet')

    soup = BeautifulSoup(html_file, features="html.parser")
    text = soup.get_text()
    text = re.sub(re.compile('<.*?>'), '', text)

    # Remove punctuation
    text = text.translate(str.maketrans('', '', punctuation))
    text = '\n'.join([line.strip()
                     for line in text.splitlines() if line.strip()])

    # Tokenize and tolower the text
    tokenized_text = word_tokenize(text, language='slovene')
    tokenized_text_lower = [word.lower() for word in tokenized_text]

    # Remove stopwords
    stopwords = set(sw.words('slovene'))
    removed_stop_words = [
        word for word in tokenized_text_lower if not word.lower() in stopwords]
    # Remove numbers and words with numbers in them
    removed_numbers = [word for word in removed_stop_words if not any(
        char.isdigit() for char in word)]

    # Lemmatize "removed numbers" with nltk  for slovene
    # Optional use lemmagen
    lemmatized_words = [nltk.stem.WordNetLemmatizer().lemmatize(word)
                        for word in removed_numbers]
    normalized_text = [
        word if word not in punctuation else "PUNCT" for word in tokenized_text_lower]

    return lemmatized_words, normalized_text
