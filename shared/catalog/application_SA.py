from flask import Flask, redirect, render_template, request, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Authors, Genres, Books

app = Flask(__name__)

engine = create_engine('postgres://vagrant:abcd@localhost/catalog')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

###  QUERIES  ###
q_genres =  '''
    SELECT DISTINCT genre
    FROM genres;
    '''

q_latest_books = '''
    SELECT books.title, genres.genre
    FROM books
    LEFT JOIN genres
        ON books.genre_id = genres.id
    ORDER BY date_finished DESC;
    '''

q_genre_books = '''
    SELECT DISTINCT books.title
    FROM books
    LEFT JOIN genres
        ON books.genre_id = genres.id
    WHERE LOWER(genres.genre)='{}'
    ORDER BY title DESC;
    '''

q_book_info = '''
    SELECT title, pages, authors.first_name || ' ' || authors.last_name, synopsis
    FROM books
    LEFT JOIN authors
        ON books.author_id = authors.id
    WHERE books.id={}
    '''

q_get_existing_authors = '''
    SELECT DISTINCT first_name || ' ' || last_name
    FROM authors;
    '''

q_get_book_info = '''
    SELECT title, pages, authors.first_name || ' ' || authors.last_name, synopsis
    FROM books
    LEFT JOIN authors
        ON books.author_id = authors.id
    WHERE books.id={}
    '''

q_edit_book_info = '''
    SELECT  books.id
            , books.title
            , authors.last_name AS author_last_name
            , authors.first_name AS author_first_name
            , genres.genre
            , books.pages
            , books.date_finished
            , books.synopsis
    FROM books
    LEFT JOIN authors
        ON books.author_id = authors.id
    LEFT JOIN genres
        ON books.genre_id = genres.id
    WHERE books.id={}
    '''


@app.route('/')
@app.route('/catalog/')
def show_catalog():
    # Query returns a list where each row from the table is a tuple.
    genres = session.execute(q_genres)
    genres = sorted([i[0] for i in genres])
    
    latest_books = session.execute(q_latest_books)
    return render_template('catalog.html', main_page=True, genres=genres, latest_books=latest_books)


@app.route('/catalog/<genre>/items/', methods=['GET'])
def genre_items(genre):
    genres = session.execute(q_genres)
    genres = sorted([i[0] for i in genres])
    items = session.execute(q_genre_books.format(genre))
    items = list(items)
    count = len(items)
    genre = genre.capitalize()

    return render_template('catalog.html', 
                            genres=genres, 
                            genre=genre, 
                            items=items,
                            count=count)


@app.route('/catalog/<genre>/<int:book_id>/', methods=['GET'])
def book_info(genre, book_id):
    info = list(session.execute(q_book_info.format(book_id)))
    # Returns a list containing a single tuple, so get index 0.
    info = info[0]
    return render_template('book.html', book_id=book_id, info=info)


# ADD BOOK
@app.route('/catalog/newBook/', methods=['GET', 'POST'])
def new_book():
    if request.method == 'POST':
        # EXAMPLE row:
        # 1 War and Peace   1   HIF 1225    The novel chronicles the history of the French invasion of Russia and the impact of the Napoleonic era on Tsarist society through the stories of five Russian aristocratic families.    2019-01-01        
        
        existing_authors = session.execute(q_get_existing_authors)
        existing_authors = [i[0] for i in list(existing_authors)]
        # print('EXISTING AUTHORS: ', existing_authors)
        first_name = request.form['author_first_name'].strip()
        last_name = request.form['author_last_name'].strip()
        full_name = first_name + ' ' + last_name
        # print('FULLNAME: ', full_name)

        # If author is not in 'authors', add new entry to 'authors' table
        if full_name not in existing_authors:
            new_author = Authors(last_name=request.form['author_last_name'], 
                                 first_name=request.form['author_first_name'])
            session.add(new_author)
            session.commit()

        author_id = session.execute(f"SELECT id FROM authors WHERE first_name='{first_name}' AND last_name='{last_name}';")
        author_id = list(author_id)[0][0]
        # print('AUTHOR_ID: ', author_id)
        genre_id = session.execute(f"SELECT id FROM genres WHERE genre='{request.form['genre']}';")
        genre_id = list(genre_id)[0][0]
        # print('GENRE_ID: ', genre_id)

        title = request.form['title']
        pages = request.form['pages']
        synopsis = request.form['synopsis']
        date_finished = request.form['date_finished']

        new_item = Books(
                        title=title,
                        author_id=author_id,
                        genre_id=genre_id,
                        pages=pages,
                        synopsis=synopsis,
                        date_finished=date_finished)

        try:
            session.add(new_item)
            session.commit()

            new_book_id = session.execute(f"SELECT MAX(id) FROM books;")
            new_book_id = list(new_book_id)[0][0]

            info = session.execute(q_get_book_info.format(new_book_id))
            info = [i for i in list(info)[0]]
            flash('New book added!')
            return render_template('book.html', info=info)

        except Exception as error:
            session.rollback()
            raise

    else:
        genres = session.execute(q_genres)
        genres = sorted([i[0] for i in genres])
        return render_template('newBook.html', genres=genres)



def lookup_author_id(first_name, last_name):
    result = session.execute('''
        SELECT id
        FROM authors
        WHERE last_name = '{}' AND
        first_name = '{}';
        '''.format(last_name, first_name))
    return list(result)[0][0]


def lookup_genre_id(genre):
    print('arg genre:', genre)
    result = session.execute('''
        SELECT id
        FROM genres
        WHERE genre = '{}';
        '''.format(genre))
    result = list(result)[0][0]
    print(type(result))
    return result


def add_author(first_name, last_name):
    new_author = Authors(first_name=first_name, last_name=last_name)
    session.add(new_author)
    session.commit()
    return session.execute(f"SELECT MAX(id) FROM authors;")



# EDIT BOOK
@app.route('/catalog/<genre>/<int:book_id>/edit', methods=['GET', 'POST'])
def edit_book(genre, book_id):
    book = session.query(Books).filter_by(id=book_id).one()
    
    if request.method == 'POST':
        
        # Then the queried row gets that new 'name' value.
        book.title = request.form['title']

        first_name = request.form['author_first_name'].strip()
        last_name = request.form['author_last_name'].strip()
        existing_author_id = lookup_author_id(first_name, last_name)
        if existing_author_id:
            book.author_id = existing_author_id
        else:
            new_author_id = add_author(first_name, last_name)
            book.author_id = new_author_id

        genre = request.form['genre']
        print("GENRE from form: ", genre)
        book.genre_id = lookup_genre_id(genre)
        
        book.pages = request.form['pages']
        book.synopsis = request.form['synopsis']
        book.date_finished = request.form['date_finished']
        
        try:        
            session.add(book)
            session.commit()
            flash('Book successfully edited!')
            print('flash should have happened just now')
            
            info = list(session.execute(q_book_info.format(book_id)))
            # Returns a list containing a single tuple, so get index 0.
            info = info[0]
            return render_template('book.html', book_id=book_id, info=info)

        except Exception as error:
            session.rollback()
            raise

    else:
        edit_book_info = session.execute(q_edit_book_info.format(book_id))
        edit_book_info = list(edit_book_info)
        edit_book_info = [i for i in edit_book_info[0]]
        print(edit_book_info)

        book_info = {}
        book_info['id'] = edit_book_info[0]
        book_info['title'] = edit_book_info[1]
        book_info['author_last_name'] = edit_book_info[2]
        book_info['author_first_name'] = edit_book_info[3]
        book_info['genre'] = edit_book_info[4]
        book_info['pages'] = edit_book_info[5]
        book_info['date_finished'] = edit_book_info[6]
        book_info['synopsis'] = edit_book_info[7]

        genres = session.execute(q_genres)
        genres = sorted([i[0] for i in genres])

        return render_template('editBook.html', book_info=book_info, genres=genres)


# DELETE BOOK
@app.route('/catalog/<genre>/<int:book_id>/delete', methods=['GET', 'POST'])
def delete_book(genre, book_id):
    book = session.query(Books).filter_by(id=book_id).one()
    if request.method == 'POST':
        session.delete(book)
        session.commit()
        flash('Book successfully DELETED!')
        return redirect(url_for('genre_items', genre=genre))
    else:
        info = list(session.execute(q_book_info.format(book_id)))
        # Returns a list containing a single tuple, so get index 0.
        info = info[0]
        return render_template('deleteBook.html', genre=genre, book_id=book_id, info=info)



if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.run(host='0.0.0.0', port=8000, debug=True)

