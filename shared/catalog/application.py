from flask import Flask, redirect, render_template, request, url_for, flash, jsonify, make_response
from flask import session as login_session
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Authors, Genres, Books, Users
import random, string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = 'My Books Catalog Application'

# Connect to postgres database and create database session.
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
    SELECT books.title, genres.genre, books.id
    FROM books
    LEFT JOIN genres
        ON books.genre_id = genres.id
    WHERE books.user_id = {}
    ORDER BY date_finished DESC;
    '''

q_genre_books = '''
    SELECT DISTINCT books.title, books.id
    FROM books
    LEFT JOIN genres
        ON books.genre_id = genres.id
    WHERE LOWER(genres.genre)='{}'
      AND books.user_id = {}
    ORDER BY title DESC;
    '''

q_book_info = '''
    SELECT title
        , pages
        , authors.first_name || ' ' || authors.last_name
        , synopsis
        , date_finished
    FROM books
    LEFT JOIN authors
        ON books.author_id = authors.id
    WHERE books.id = {};
    '''

q_get_existing_authors = '''
    SELECT DISTINCT first_name || ' ' || last_name
    FROM authors
    WHERE user_id = {};
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
      AND books.user_id = {};
    '''


### LOGIN
@app.route('/login')
def showLogin():
    # Create anti-forgery state token
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'], 'flash')

    print('LOGIN_SESSION: ',login_session)
    return render_template('catalog.html', flash=flash)

# User Helper Functions
def createUser(login_session):
    name_parts = login_session['username'].split(' ')
    newUser = Users(last_name=name_parts[-1],
                    first_name=name_parts[0],
                    email=login_session['email'], 
                    picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(Users).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(Users).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(Users).filter_by(email=email).one()
        return user.id
    except:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session

@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print('In gdisconnect access token is %s', access_token)
    print('User name is: ')
    print(login_session['username'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print('result is ')
    print(result)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash('Successfully logged out.')
        return redirect(url_for('show_catalog'))
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


### JSON API ENDPOINTS
@app.route('/catalog/<genre>/<int:book_id>/json')
def books_json(genre, book_id):
    # Check if user is logged in
    if 'username' not in login_session:
        return render_template('public.html', genres=genres)

    books = session.query(Books).filter_by(id=book_id).all()
    return jsonify(Books=[i.serialize for i in books])


@app.route('/catalog/json')
def catalog_json():
    # Check if user is logged in
    if 'username' not in login_session:
        return render_template('public.html', genres=genres)

    items = session.query(Books).all()
    return jsonify(Books=[i.serialize for i in items])


### APP PAGES
@app.route('/')
@app.route('/catalog/')
def show_catalog():
    # Query returns a list where each row from the table is a tuple.
    genres = session.execute(q_genres)
    genres = sorted([i[0] for i in genres])

    # Check if user is logged in
    if 'username' not in login_session:
        return render_template('public.html', genres=genres)

    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    latest_books = session.execute(q_latest_books.format(user_id))    
    return render_template('catalog.html', main_page=True, genres=genres, latest_books=latest_books)


@app.route('/catalog/<genre>/items/', methods=['GET'])
def genre_items(genre):
    # Check if user is logged in
    if 'username' not in login_session:
        return render_template('public.html', genres=genres)

    genres = session.execute(q_genres)
    genres = sorted([i[0] for i in genres])
    genre = genre.lower()

    user_id = getUserID(login_session['email'])
    items = session.execute(q_genre_books.format(genre, user_id))
    items = sorted(list(items))
    count = len(items)
    # Re-capitalize 'genre' for the heading on the page.
    genre = genre.capitalize()

    return render_template('catalog.html', 
                            main_page=False,
                            genres=genres, 
                            genre=genre, 
                            items=items,
                            count=count)


@app.route('/catalog/<genre>/<int:book_id>/', methods=['GET'])
def book_info(genre, book_id):
    # Check if user is logged in
    if 'username' not in login_session:
        return render_template('public.html', genres=genres)

    user_id = getUserID(login_session['email'])
    info = list(session.execute(q_book_info.format(book_id, user_id)))
    # Returns a list containing a single tuple, so get index 0.
    info = info[0]
    return render_template('book.html', genre=genre, book_id=book_id, info=info)


# ADD BOOK
@app.route('/catalog/newBook/', methods=['GET', 'POST'])
def new_book():
    # Check if user is logged in
    if 'username' not in login_session:
        return render_template('public.html', genres=genres)

    genres = session.execute(q_genres)
    genres = sorted([i[0] for i in genres])

    if request.method == 'POST':
        # EXAMPLE row:
        # 1 War and Peace   1   HIF 1225    The novel chronicles the history of the French invasion of Russia and the impact of the Napoleonic era on Tsarist society through the stories of five Russian aristocratic families.    2019-01-01        
        user_id = getUserID(login_session['email'])
        existing_authors = session.execute(q_get_existing_authors.format(user_id))
        existing_authors = [i[0] for i in list(existing_authors)]
        first_name = request.form['author_first_name'].strip()
        last_name = request.form['author_last_name'].strip()
        full_name = first_name + ' ' + last_name

        # If author is not in 'authors', add new entry to 'authors' table
        if full_name not in existing_authors:
            new_author = Authors(last_name=request.form['author_last_name'], 
                                 first_name=request.form['author_first_name'])
            session.add(new_author)
            session.commit()

        author_id = session.execute(f"SELECT id FROM authors WHERE first_name='{first_name}' AND last_name='{last_name}';")
        author_id = list(author_id)[0][0]
        genre_id = session.execute(f"SELECT id FROM genres WHERE genre='{request.form['genre']}';")
        genre_id = list(genre_id)[0][0]
        title = request.form['title']
        pages = request.form['pages']
        synopsis = request.form['synopsis']
        date_finished = request.form['date_finished']

        new_item = Books(title=title,
                        author_id=author_id,
                        genre_id=genre_id,
                        pages=pages,
                        synopsis=synopsis,
                        date_finished=date_finished,
                        user_id=user_id)
        
        try:
            session.add(new_item)
            session.commit()

            new_book_id = session.execute(f"SELECT MAX(id) FROM books;")
            new_book_id = list(new_book_id)[0][0]

            user_id = getUserID(login_session['email'])
            print('USERID',user_id)
            info = session.execute(q_book_info.format(new_book_id, user_id))
            print(info)
            info = [i for i in list(info)[0]]
            print(info)
            flash(f'New book added: {info[0]}')
            return render_template('book.html', info=info, book_id=new_book_id)

        except exc.IntegrityError as e:
            session.rollback()
            flash(f'Error! You already have this book-author pairing: {title} by {first_name} {last_name}.')
            return redirect(url_for('new_book'))

    else:        
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
    result = session.execute('''
        SELECT id
        FROM genres
        WHERE genre = '{}';
        '''.format(genre))
    result = list(result)[0][0]
    return result


def add_author(first_name, last_name):
    new_author = Authors(first_name=first_name, last_name=last_name)
    session.add(new_author)
    session.commit()
    return session.execute(f"SELECT MAX(id) FROM authors;")



# EDIT BOOK
@app.route('/catalog/<genre>/<int:book_id>/edit', methods=['GET', 'POST'])
def edit_book(genre, book_id):
    # Check if user is logged in
    if 'username' not in login_session:
        return render_template('public.html', genres=genres)

    book = session.query(Books).filter_by(id=book_id).one()
    
    if request.method == 'POST':
        
        # Then the queried row gets that new 'name' value.
        entered_title = request.form['title']
        book.title = entered_title

        first_name = request.form['author_first_name'].strip()
        last_name = request.form['author_last_name'].strip()
        existing_author_id = lookup_author_id(first_name, last_name)
        if existing_author_id:
            book.author_id = existing_author_id
        else:
            new_author_id = add_author(first_name, last_name)
            book.author_id = new_author_id

        genre = request.form['genre']
        book.genre_id = lookup_genre_id(genre)
        
        book.pages = request.form['pages']
        book.synopsis = request.form['synopsis']
        book.date_finished = request.form['date_finished']
        
        try:        
            session.add(book)
            session.commit()
            flash('Book successfully edited!')
            
            user_id = getUserID(login_session['email'])
            info = list(session.execute(q_book_info.format(book_id, user_id)))
            # Returns a list containing a single tuple, so get index 0.
            info = info[0]
            return render_template('book.html', book_id=book_id, info=info)

        except exc.IntegrityError as e:
            session.rollback()
            session.flush()
            flash(f'Error! You already have this book-author pairing: {entered_title} by {first_name} {last_name}.')
            return redirect(url_for('edit_book', genre=genre, book_id=book_id))

    else:
        user_id = getUserID(login_session['email'])
        edit_book_info = session.execute(q_edit_book_info.format(book_id, user_id))
        edit_book_info = list(edit_book_info)
        edit_book_info = [i for i in edit_book_info[0]]

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
    # Check if user is logged in
    if 'username' not in login_session:
        return render_template('public.html', genres=genres)

    book = session.query(Books).filter_by(id=book_id).one()
    if request.method == 'POST':
        session.delete(book)
        session.commit()
        flash('Book successfully DELETED!')
        return redirect(url_for('genre_items', genre=genre))
    else:        
        user_id = getUserID(login_session['email'])
        info = list(session.execute(q_book_info.format(book_id, user_id)))
        # Returns a list containing a single tuple, so get index 0.
        info = info[0]
        return render_template('deleteBook.html', genre=genre, book_id=book_id, info=info)




if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.run(host='0.0.0.0', port=8000, debug=True)
