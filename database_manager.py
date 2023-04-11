# Importing libraries
import sqlite3
from flask import current_app,g


class DataBaseManager():
    def __init__(self):
        # Database path
        self.path_DB = current_app.config['DATABASE']
        self.path_DB_SCHEMA = current_app.config['DATABASE_SCHEMA']
        self.create_database()
    
    # Database connection
    def get_db(self):
        db = getattr(g, '_database', None)
        if db is None:
            db = g._database = sqlite3.connect(self.path_DB)
        print("Database connected successfully")
        return db
    
    # create database if not exist
    def create_database(self):
        '''
        This function will create database if not exist
        '''
        db = self.get_db()
        with open(self.path_DB_SCHEMA) as f:
            db.executescript(f.read())
        db.commit()
        print("Try Table created if not exist")