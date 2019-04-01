from flask import Flask, request, redirect, url_for, render_template
from catalog_db import get_all, get_genres, get_genre_items, get_latest_books, get_book_info

app = Flask(__name__)

@app.route('/', methods=['GET'])
@app.route('/catalog', methods=['GET'])
def show_catalog():
    # Query returns a list where each row from the table is a tuple.
    genres = get_genres()
    genres = [i[0] for i in genres]
    latest_books = get_latest_books()
    return render_template('catalog.html', main_page=True, genres=genres, latest_books=latest_books)


@app.route('/catalog/<genre>/items', methods=['GET'])
def genre_items(genre):
    genres = get_genres()
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


@app.route('/catalog/<genre>/<book_title>', methods=['GET'])
def book_info(genre, book_title):
    book_title = book_title.lower()
    info = get_book_info(book_title)
    print(info)
    return render_template('book.html', book_title=book_title, info=info)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
