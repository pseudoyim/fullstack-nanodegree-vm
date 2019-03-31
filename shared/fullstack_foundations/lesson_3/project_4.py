from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem
app = Flask(__name__)

engine = create_engine('sqlite:///restaurantmenu.db') 	# Generates and saves database file in current working directory with this name.
Base.metadata.create_all(engine)

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/restaurants/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
	items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
	output = ''
	for i in items:
		output += i.name + '</br>'
		output += i.price + '</br>'
		output += i.description + '</br>'
		output += '</br>'

	return output

if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0', port=5000)
