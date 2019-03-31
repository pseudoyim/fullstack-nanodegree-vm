import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Restaurant(Base):
	__tablename__ = 'restaurant'
	name = Column(String(80), nullable = False)
	id = Column(Integer, primary_key = True)


class MenuItem(Base):
	__tablename__ = 'menu_item'
	name = Column(String(80), nullable = False)
	id = Column(Integer, primary_key = True)
	course = Column(String(250))
	description = Column(String(250))
	price = Column(String(8))	
	restaurant = relationship(Restaurant)
	restaurant_id = Column(Integer, ForeignKey('restaurant.id'))

	# This function allows us to send JSON objects in a serializable format.
	@property
	def serialize(self):
		return {
			'name': self.name,
			'description': self.description,
			'id': self.id,
			'price': self.price,
			'course': self.course,
		}


engine = create_engine('sqlite:///restaurantmenu.db', connect_args={'check_same_thread': False}) 	# Generates and saves database file in current working directory with this name.
Base.metadata.create_all(engine)

