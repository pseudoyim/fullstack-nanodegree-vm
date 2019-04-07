--
-- PostgreSQL database dump
-- From command line, run:
-- >>> createdb catalog
-- >>> psql catalog < <path to this file: catalog.sql>
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = public, pg_catalog;
SET default_tablespace = '';
SET default_with_oids = false;


-- 'authors'
CREATE TABLE IF NOT EXISTS authors (full_name TEXT PRIMARY KEY,
									last_name TEXT, 
									first_name TEXT );

-- 'genres'
CREATE TABLE IF NOT EXISTS genres (	id TEXT PRIMARY KEY,
									genre TEXT );

-- 'books'
CREATE TABLE IF NOT EXISTS books (  id SERIAL PRIMARY KEY,
									title TEXT, 
									author TEXT,
									genre_id TEXT,
									pages INTEGER,
									synopsis TEXT,
									date_finished DATE,
									UNIQUE (title, author));

-- Modify initial value and increment
ALTER SEQUENCE books_id_seq RESTART WITH 4;


-- 'books' data (each row must be tab-delimited)
COPY authors (full_name, last_name, first_name) FROM stdin;
Leo Tolstoy	Tolstoy	Leo
Mark Twain	Twain	Mark
\.

-- 'genres' data
COPY genres (id, genre) FROM stdin;
NOV	Novel
FIC	Fiction
BIO	Biography
MYS	Mystery
ROM	Romance
SCI	Science Fiction
SOC	Sociology
PHI	Philosophy
\.

-- 'books' data
COPY books (id, title, author, genre_id, pages, synopsis, date_finished) FROM stdin;
1	War and Peace	Leo Tolstoy	FIC	1225	The novel chronicles the history of the French invasion of Russia and the impact of the Napoleonic era on Tsarist society through the stories of five Russian aristocratic families.	2019-01-01
2	Anna Kerenina	Leo Tolstoy	NOV	864	A complex novel in eight parts, with more than a dozen major characters, it is spread over more than 800 pages (depending on the translation), typically contained in two volumes. It deals with themes of betrayal, faith, family, marriage, Imperial Russian society, desire, and rural vs. city life. 	2019-02-01
3	The Adventures of Tom Sawyer	Mark Twain	NOV	274	about a young boy growing up along the Mississippi River. It is set in the 1840s in the fictional town of St. Petersburg, inspired by Hannibal, Missouri, where Twain lived as a boy. In the novel Tom Sawyer has several adventures, often with his friend, Huckleberry Finn.	2019-03-01
\.
