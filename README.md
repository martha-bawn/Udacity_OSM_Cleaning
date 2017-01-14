# Udacity_OSM_Cleaning
Project 3 for Udacity Data Analyst Nanodegree  
Data Wrangling course

## Description
In this assignment, I took a section of the world (my hometown of Boulder, Colorado and 
it's surrounding area) from OpenStreetMaps, cleaned it using Python, put it into a SQLite 
database and explored it with some simple queries.

## Files
- The ipynb file contains snippets of code, queries, and the report.  
- The html file is the final report, including code snippets and discussion.  
- csv_schema.py is the schema for the database, and was taken directly from Udacity's 
materials 
- get_sample.py creates a small osm data file for testing code, and it was directly
from Udacity's materials
- data.py contains all the data cleaning code, including tests, some of which was adapted
from Udacity's course exercises. It reads the osm files, applies the cleaning functions,
and writes the cleaned data into csv files
- sql_database.py inserts cleaned csv files into SQL database and runs queries
