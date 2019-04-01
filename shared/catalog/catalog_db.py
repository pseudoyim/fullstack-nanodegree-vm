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


def get_genres():
    db = psycopg2.connect(f"dbname={DBNAME}")
    c = db.cursor()
    query = '''
            SELECT DISTINCT genre
            FROM books;
            '''
    c.execute(query)
    result = c.fetchall()
    db.close()
    return result


def get_latest_books():
    db = psycopg2.connect(f"dbname={DBNAME}")
    c = db.cursor()
    query = '''
            SELECT title, genre
            FROM books
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
            SELECT DISTINCT title
            FROM books
            WHERE LOWER(genre)='{genre}'
            ORDER BY title DESC;
            '''
    c.execute(query)
    result = c.fetchall()
    db.close()
    return result


def get_book_info(book_title):
    db = psycopg2.connect(f"dbname={DBNAME}")
    c = db.cursor()
    query = f'''
            SELECT title, pages, authors.first_name || ' ' || authors.last_name, synopsis
            FROM books
            LEFT JOIN authors
                ON books.author_id = authors.id
            WHERE LOWER(title)='{book_title}'
            '''
    c.execute(query)
    result = c.fetchall()
    db.close()
    return result


if __name__ == '__main__':
    get_books()