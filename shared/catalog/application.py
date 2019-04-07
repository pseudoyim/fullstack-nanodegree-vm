from flask import Flask, redirect, render_template, request, url_for, flash, jsonify
from catalog_db import  get_all, \
                        get_all_authors, \
                        get_all_genres, \
                        get_genres_table, \
                        get_genre_items, \
                        get_latest_books, \
                        get_book_info, \
                        insert_author, \
                        insert_book, \
                        insert_genre

app = Flask(__name__)

@app.route('/', methods=['GET'])
@app.route('/catalog/', methods=['GET'])
def show_catalog():
    # Query returns a list where each row from the table is a tuple.
    genres = get_all_genres()
    genres = [i[0] for i in genres]
    latest_books = get_latest_books()
    return render_template('catalog.html', main_page=True, genres=genres, latest_books=latest_books)


@app.route('/catalog/<genre>/items/', methods=['GET'])
def genre_items(genre):
    genres = get_all_genres()
    genres = [i[0] for i in genres]
    items = get_genre_items(genre)
    count = len(items)
    genre = genre.capitalize()
    return render_template('catalog.html', 
                        main_page=False, 
                        genres=genres, 
                        genre=genre, 
                        items=items,
                        count=count)


@app.route('/catalog/<genre>/<int:book_id>/', methods=['GET'])
def book_info(genre, book_id):
    # Returns a list containing a single tuple, so get index 0.
    info = get_book_info(book_id)[0]
    return render_template('book.html', book_id=book_id, info=info)


# ADD BOOK
@app.route('/catalog/newBook/', methods=['GET', 'POST'])
def new_book():
    if request.method == 'POST':
        # EXAMPLE row:
        # 1 War and Peace   1   HIF 1225    The novel chronicles the history of the French invasion of Russia and the impact of the Napoleonic era on Tsarist society through the stories of five Russian aristocratic families.    2019-01-01
        
        # If author is not in 'authors', add new entry to 'authors' table
        existing_authors = [i[0] for i in get_all_authors()]
        print(existing_authors)

        first_name = request.form['author_first_name'].strip()
        last_name = request.form['author_last_name'].strip()
        full_name = first_name + ' ' + last_name

        if full_name not in existing_authors:
            insert_author(full_name, last_name, first_name)

        title = request.form['title']
        author = first_name + ' ' + last_name

        #

        genres_raw = get_genres_table()
        genres_dict = {}
        for i in genres_raw:
            genres_dict[i[1]] = i[0]

        genre = request.form['genre'].strip()
        print(f'GENRE:-{genre}-')
        genre_id = genres_dict[genre]
        print('GENRE_ID: ', genre_id)

        pages = request.form['pages']
        synopsis = request.form['synopsis']
        date_finished = request.form['date_finished']

        book_content = [title, author, genre_id, pages, synopsis, date_finished]
        print('book_content!')
        print(book_content)
        new_book_id = insert_book(book_content)
        new_book_id = new_book_id[0][0]
        info = get_book_info(new_book_id)[0]
        

        return render_template('book.html', info=info)
    else:
        genres = [i[0] for i in get_all_genres()]
        genres = sorted(genres)
        return render_template('newBook.html', genres=genres)





# EDIT BOOK

# DELETE BOOK


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)

