# "Database code" for the DB Forum.

import bleach
import datetime
import psycopg2

DBNAME = 'catalog'

def get_all():
    """Return all posts from the database"""
    db = psycopg2.connect(f"dbname={DBNAME}")
    c = db.cursor()
    query = '''
            SELECT *
            FROM books;
            '''
    c.execute(query)
    result = c.fetchall()
    db.close()
    return result


def get_all_authors():
    db = psycopg2.connect(f"dbname={DBNAME}")
    c = db.cursor()
    query = '''
            SELECT DISTINCT first_name || ' ' || last_name
            FROM authors;
            '''
    c.execute(query)
    result = c.fetchall()
    db.close()
    return result

def get_all_genres():
    db = psycopg2.connect(f"dbname={DBNAME}")
    c = db.cursor()
    query = '''
            SELECT DISTINCT genre
            FROM genres;
            '''
    c.execute(query)
    result = c.fetchall()
    db.close()
    return result


def get_genres_table():
    db = psycopg2.connect(f"dbname={DBNAME}")
    c = db.cursor()
    query = '''
            SELECT *
            FROM genres;
            '''
    c.execute(query)
    result = c.fetchall()
    db.close()
    return result

def get_latest_books():
    db = psycopg2.connect(f"dbname={DBNAME}")
    c = db.cursor()
    query = '''
            SELECT books.title, genres.genre
            FROM books
            LEFT JOIN genres
                ON books.genre_id = genres.id
            ORDER BY date_finished DESC;
            '''
    c.execute(query)
    result = c.fetchall()
    db.close()
    return result


def get_genre_items(genre):
    db = psycopg2.connect(f"dbname={DBNAME}")
    c = db.cursor()
    query = f'''
            SELECT DISTINCT books.title
            FROM books
            LEFT JOIN genres
                ON books.genre_id = genres.id
            WHERE LOWER(genres.genre)='{genre}'
            ORDER BY title DESC;
            '''
    c.execute(query)
    result = c.fetchall()
    db.close()
    return result


def get_book_info(book_id):
    db = psycopg2.connect(f"dbname={DBNAME}")
    c = db.cursor()
    query = f'''
            SELECT title, pages, authors.first_name || ' ' || authors.last_name, synopsis
            FROM books
            LEFT JOIN authors
                ON books.author = authors.full_name
            WHERE books.id={book_id}
            '''
    c.execute(query)
    result = c.fetchall()
    db.close()
    return result


def insert_author(full_name, last_name, first_name):
    db = psycopg2.connect(f"dbname={DBNAME}")
    c = db.cursor()
    full_name = bleach.clean(full_name)
    last_name = bleach.clean(last_name)
    first_name = bleach.clean(first_name)
    c.execute(f"INSERT INTO authors(full_name, last_name, first_name) values ('{full_name}', '{last_name}', '{first_name}')")
    db.commit()
    db.close()

def insert_book(content):
    # 1 War and Peace   Leo Tolstoy   HIF 1225    The novel chronicles the history of the French invasion of Russia and the impact of the Napoleonic era on Tsarist society through the stories of five Russian aristocratic families.    2019-01-01
    print('************** CONTENT:', content)
    
    bleached = []
    for i in content:
        b = bleach.clean(i).strip()
        bleached.append(b)

    title, author, genre_id, pages, synopsis, date_finished = bleached

    db = psycopg2.connect(f"dbname={DBNAME}")
    c = db.cursor()
    c.execute(f"INSERT INTO books(title, author, genre_id, pages, synopsis, date_finished) \
                values ('{title}', '{author}', '{genre_id}', {pages}, '{synopsis}', '{date_finished}') \
                RETURNING id;")
    new_book_id = c.fetchall()
    db.commit()
    db.close()
    return new_book_id

def insert_genre(content):
    db = psycopg2.connect(f"dbname={DBNAME}")
    c = db.cursor()
    content = bleach.clean(content)
    c.execute("INSERT INTO genre values (%s)", (bleach.clean(content),))
    db.commit()
    db.close()



if __name__ == '__main__':
    get_books()