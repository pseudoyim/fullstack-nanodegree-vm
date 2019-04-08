import sys
from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Authors(Base):
	__tablename__ = 'authors'
	id = Column(Integer, primary_key=True)
	last_name = Column(String(100))
	first_name = Column(String(100))


class Genres(Base):
	__tablename__ = 'genres'
	id = Column(String(4), primary_key=True)
	genre = Column(String(100))


class Books(Base):
	__tablename__ = 'books'
	id = Column(Integer, primary_key=True)
	title = Column(String(100), nullable=False)
	authors = relationship(Authors)
	author_id = Column(Integer, ForeignKey('authors.id'))
	genres = relationship(Genres)
	genre_id = Column(Integer, ForeignKey('genres.id'))
	pages = Column(Integer)
	synopsis = Column(String(500))
	date_finished = Column(Date)


engine = create_engine('postgres://vagrant:abcd@localhost/catalog')
Base.metadata.create_all(engine)
