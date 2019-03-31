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


def add_post(content):
    """Add a post to the 'database' with the current timestamp."""
    db = psycopg2.connect(f"dbname={DBNAME}")
    c = db.cursor()
    content = bleach.clean(content)
    c.execute("insert into books values (%s)", (bleach.clean(content),))  # good
    db.commit()
    db.close()


if __name__ == '__main__':
    get_books()