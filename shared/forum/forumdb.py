# "Database code" for the DB Forum.


import bleach
import datetime
import psycopg2

DBNAME = 'forum'

def get_posts():
    """Return all posts from the 'database', most recent first."""
    db = psycopg2.connect(f"dbname={DBNAME}")
    c = db.cursor()
    query = '''
            SELECT content, time 
            FROM posts 
            ORDER BY time DESC;
            '''
    c.execute(query)
    posts = c.fetchall()
    db.close()
    return posts


def add_post(content):
    """Add a post to the 'database' with the current timestamp."""

    db = psycopg2.connect(f"dbname={DBNAME}")
    c = db.cursor()
    content = bleach.clean(content)
    c.execute("insert into posts values (%s)", (bleach.clean(content),))  # good
    db.commit()
    db.close()