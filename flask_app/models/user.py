from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash, app

import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class User:
    def __init__(self,data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        # below is the empty place to store all the sightings this user has logged
        self.sightings = []
        self.skeptical = []

    @classmethod
    def add_user(cls,data):
        query = 'INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password)s, NOW(), NOW());'
        return connectToMySQL('sasquatch_sightings_schema').query_db(query,data)
    
    @classmethod
    def get_user(cls,data):
        query = 'SELECT * FROM users WHERE id = %(id)s;'
        return connectToMySQL('sasquatch_sightings_schema').query_db(query,data)

    @classmethod
    def get_all(cls,data):
        query = 'SELECT * FROM users;'
        return connectToMySQL('sasquatch_sightings_schema').query_db(query,data)

    @classmethod
    def get_by_email(cls,data):
        query = 'SELECT * FROM sasquatch_sightings_schema.users WHERE users.email = %(email)s;'
        result = connectToMySQL('sasquatch_sightings_schema').query_db(query,data)
        if len(result) < 1:
            return False
        return cls(result[0])

    @staticmethod
    def validate_registration(user):
        is_valid = True
        if not EMAIL_REGEX.match(user['email']):
            flash('Please enter a valid email address.', 'register')
            is_valid = False
        if len(user['fname']) < 2:
            flash('First name must be at least 2 characters', 'register')
            is_valid = False
        if len(user['lname']) < 2:
            flash('Last name must be at least 2 characters', 'register')
            is_valid = False
        if user['password'] != user['confirm_password']:
            flash('Passwords must match', 'register')
            is_valid = False
        if len(user['password']) < 8:
            flash('Password must be at least 8 characters', 'register')
            is_valid = False
        return is_valid

    @staticmethod
    def validate_login(user):
        is_valid = True
        if not EMAIL_REGEX.match(user['email']):
            flash('Please enter a valid email address.', 'login')
            is_valid = False
        return is_valid