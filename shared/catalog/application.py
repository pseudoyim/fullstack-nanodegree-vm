from flask import Flask, request, redirect, url_for, render_template
from catalog_db import get_all, get_genres

app = Flask(__name__)

@app.route('/', methods=['GET'])
@app.route('/catalog', methods=['GET'])
def show_catalog():
  # Query result is a list where each row is a tuple.
  genres = list(get_genres())
  genres = sorted(genres)

  return render_template('catalog.html', genres=genres)






if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8000, debug=True)
