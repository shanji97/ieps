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
    try:
        cursor.executemany('INSERT INTO IndexWord VALUES (?);', list(
            set([(item[0], ) for item in insert_dict.keys()])))
        cursor.executemany(
            'INSERT INTO Posting VALUES (?, ?, ?, ?);', insert_dict.values())
        conn.commit()
    except Exception:
        pass



def tokenize_html_text(html):
    """
        Used for sqlite query indexes
    """
    soup = BeautifulSoup(html, features="html.parser")
    text = soup.get_text()
    text = re.sub(re.compile('<.*?>'), '', text)
    text = '\n'.join([line.strip() for line in text.splitlines() if line.strip()])
    return word_tokenize(text, language='slovene')

def normalize_text(html_file):
    # NLTK downloads
    # nltk.download('punkt')
    # nltk.download('stopwords')
    # nltk.download('wordnet')

    tokenized_text = tokenize_html_text(html_file)

    # To lowercase
    normalized_text = [word.lower() for word in tokenized_text]

    # Remove punct
    normalized_text = [word if word not in punctuation else "PUNCT" for word in normalized_text]

    # Remove stopwords
    stopwords = set(sw.words('slovene'))
    normalized_text = [word if word.lower() not in list(stopwords) else "STOPWORD" for word in normalized_text]

    # Remove numbers and words with numbers in them
    normalized_text = [word if not any(char.isdigit() for char in word) else "NUM" for word in normalized_text]

    # Lemmatize "removed numbers" with nltk  for slovene
    # Optional use lemmagen
    normalized_text = [nltk.stem.WordNetLemmatizer().lemmatize(word) for word in normalized_text]

    return tokenized_text, normalized_text
