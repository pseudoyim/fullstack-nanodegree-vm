from flask import Flask, request, redirect, url_for, render_template
from database_setup import item, items, restaurant, restaurants

app = Flask(__name__)

@app.route('/', methods=['GET'])
@app.route('/restaurants', methods=['GET'])
def show_restaurants():
  '''Main page.'''
  content = 'This page will show all my restaurants.'
  return render_template('restaurants.html', restaurants=restaurants, restaurant=restaurant)


@app.route('/restaurant/new', methods=['GET', 'POST'])
def new_restaurant():
  if request.method == 'POST':
    pass
  else:
    return render_template('newRestaurant.html')


@app.route('/restaurant/<int:restaurant_id>/edit', methods=['GET', 'POST'])
def edit_restaurant(restaurant_id):
  if request.method == 'POST':
    pass
  else:
    return render_template('editRestaurant.html', restaurant_id=restaurant_id)


@app.route('/restaurant/<int:restaurant_id>/delete', methods=['GET', 'POST'])
def delete_restaurant(restaurant_id):
  if request.method == 'POST':
    pass
  else:
    restaurant = restaurants[restaurant_id]
    return render_template('deleteRestaurant.html', restaurant=restaurant)


@app.route('/restaurant/<int:restaurant_id>', methods=['GET'])
@app.route('/restaurant/<int:restaurant_id>/menu', methods=['GET'])
def show_menu(restaurant_id):
  menu_len = len(items)
  restaurant = restaurants[restaurant_id]
  return render_template('menu.html', restaurant=restaurant, items=items, menu_len=menu_len)


@app.route('/restaurant/<int:restaurant_id>/menu/new', methods=['GET', 'POST'])
def new_menu_item(restaurant_id):
  if request.method == 'POST':
    pass
  else: 
    return render_template('newMenuItem.html', restaurant_id=restaurant_id)


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit', methods=['GET'])
def edit_menu_item(restaurant_id, menu_id):
  item = items[menu_id]
  return render_template('editMenuItem.html', item=item, restaurant_id=restaurant_id)


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete', methods=['GET', 'POST'])
def delete_menu_item(restaurant_id, menu_id):
  if request.method == 'POST':
    pass
  else: 
    return render_template('newMenuItem.html', restaurant_id=restaurant_id)



if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8000, debug=True)
