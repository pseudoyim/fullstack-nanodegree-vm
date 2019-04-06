from flask import Flask, request, redirect, url_for, render_template
from catalog_db import get_all, get_genres, get_genre_items, get_latest_books, get_book_info

app = Flask(__name__)

@app.route('/', methods=['GET'])
@app.route('/catalog/', methods=['GET'])
def show_catalog():
    # Query returns a list where each row from the table is a tuple.
    genres = get_genres()
    genres = [i[0] for i in genres]
    latest_books = get_latest_books()
    return render_template('catalog.html', main_page=True, genres=genres, latest_books=latest_books)


@app.route('/catalog/<genre_id>/items/', methods=['GET'])
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


@app.route('/catalog/<genre>/<int:book_id>/', methods=['GET'])
def book_info(genre, book_id):
    # Returns a list containing a single tuple, so get index 0.
    info = get_book_info(book_id)[0]
    return render_template('book.html', book_id=book_id, info=info)


# Task 1: Create route for newMenuItem function here
@app.route('/restaurants/<int:restaurant_id>/new/', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    if request.method == 'POST':
        new_item = MenuItem(name=request.form['name'], restaurant_id=restaurant_id)
        session.add(new_item)
        session.commit()
        flash('New menu item created!')
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else: # method is 'GET'
        return render_template('newmenuitem.html', restaurant_id=restaurant_id)

# ADD BOOK
@app.route('/catalog/<genre>/new/', methods=['GET', 'POST'])
def new_book():
    if request.method == 'POST':
        # 1 War and Peace   1   HIF 1225    The novel chronicles the history of the French invasion of Russia and the impact of the Napoleonic era on Tsarist society through the stories of five Russian aristocratic families.    2019-01-01
        new_row = title=title
        return redirect(url_for('book.html', book_id=book_id, info=info))
    else:
        return render_template('newBook.html', )





# EDIT BOOK

# DELETE BOOK


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)


