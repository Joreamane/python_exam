from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash, app, session
from flask_app.models.user import User

class Sighting:
    def __init__(self, data):
        self.id = data['id']
        self.location = data['location']
        self.what_happened = data['what_happened']
        self.date = data['date']
        self.number = data['number']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.user_id = session['user_id']
        self.creator = None
        self.skeptics = []

    @classmethod
    def add_sighting(cls,data):
        query = 'INSERT INTO sightings (location, what_happened, date, number, user_id, created_at, updated_at) VALUES (%(location)s, %(what_happened)s, %(date)s, %(number)s, %(user_id)s, NOW(), NOW());'
        return connectToMySQL('sasquatch_sightings_schema').query_db(query,data)

    @classmethod
    def get_sightings(cls,data):
        query = 'SELECT * FROM users LEFT JOIN sightings ON sightings.user_id = users.id WHERE users.id = %(id)s;' 
        results = connectToMySQL('sasquatch_sightings_schema').query_db(query,data)
        user_sightings = []
        for row_from_db in results:
            sighting_data = {
                'id': row_from_db['sightings.id'],
                'location': row_from_db['location'],
                'what_happened': row_from_db['what_happened'],
                'date': row_from_db['date'],
                'number': row_from_db['number'],
                'created_at': row_from_db['sightings.created_at'],
                'updated_at': row_from_db['sightings.updated_at'],
                'user_id': row_from_db['user_id']
            }
            user_sightings.append(sighting_data)
        return user_sightings

    @classmethod
    def get_one(cls,data):
        query = 'SELECT * FROM sightings JOIN users ON sightings.user_id = users.id WHERE sightings.id = %(id)s;'
        return connectToMySQL('sasquatch_sightings_schema').query_db(query,data)

    @classmethod
    def update_sighting(cls,data):
        query = 'UPDATE sightings SET location=%(location)s, what_happened=%(what_happened)s, date=%(date)s, number=%(number)s, updated_at=NOW() WHERE id=%(id)s;'
        return connectToMySQL('sasquatch_sightings_schema').query_db(query,data)

    @classmethod
    def delete_sighting(cls,data):
        query = 'DELETE FROM sightings WHERE id = %(id)s;'
        return connectToMySQL('sasquatch_sightings_schema').query_db(query,data)

    @classmethod
    def get_all_with_skeptics(cls):
        query = 'SELECT * FROM sightings LEFT JOIN skeptics ON sightings.id = skeptics.sighting_id LEFT JOIN users ON users.id = skeptics.user_id;'
        results= connectToMySQL('sasquatch_sightings_schema').query_db(query)
        previous = 0
        all_sightings = []
        count = 0
        for row in results:
            if not row['id'] == previous:
                all_sightings.append(cls(row))
                u = {
                    'id' : row['users.id'],
                    'first_name' : row['first_name'],
                    'last_name' : row['last_name'],
                    'email' : row['email'],
                    'password': row['password'],
                    'created_at': row['users.created_at'],
                    'updated_at': row['users.updated_at']
                }
                all_sightings[count].skeptics.append(User(u))
                previous = row['id']
                count += 1
            else:
                u = {
                    'id' : row['user.id'],
                    'first_name' : row['first_name'],
                    'last_name' : row['last_name'],
                    'email' : row['email'],
                    'password': row['password'],
                    'created_at': row['users.created_at'],
                    'updated_at': row['users.updated_at']
                }
                all_sightings[count-1].skeptics.append(User(u))
        return all_sightings

    @classmethod
    def add_skeptic(cls,data):
        query = 'INSERT INTO skeptics (sighting_id, user_id) VALUES (%(sighting_id)s, %(user_id)s);'
        return connectToMySQL('sasquatch_sightings_schema').query_db(query,data)

    @classmethod
    def add_believer(cls,data):
        query = 'INSERT INTO believers (sighting_id, user_id) VALUES (%(sighting_id)s, %(user_id)s);'
        return connectToMySQL('sasquatch_sightings_schema').query_db(query,data)

    @classmethod
    def get_total_believers(cls):
        query = 'SELECT * FROM believers;'
        return connectToMySQL('sasquatch_sightings_schema').query_db(query)
    
    @classmethod
    def get_total_skeptics(cls):
        query = 'SELECT * FROM sightings LEFT JOIN skeptics ON sightings.id = skeptics.sighting_id LEFT JOIN skeptics ON users.id = skeptics.user_id;'
        results = connectToMySQL('sasquatch_sightings_schema').query_db(query)
        all_skeptics =[]
        for row in results:
            one_skeptic = cls(row)
            one_skeptic_info = {
                'id' : row['users.id'],
                'first_name' : row['first_name'],
                'last_name' : row['last_name'],
                'email' : row['email'],
                'password' : row['password'],
                'created_at' : row['users.created_at'],
                'updated_at' : row['users.updated_at']
            }
            skeptic = User(one_skeptic_info)
            all_skeptics.append(skeptic)
        return all_skeptics

    @classmethod
    def get_all_sightings_with_creator(cls):
        query = 'SELECT * FROM sightings JOIN users ON sightings.user_id = users.id;'
        results = connectToMySQL('sasquatch_sightings_schema').query_db(query)
        all_sightings = []
        for row in results:
            one_sighting = cls(row)
            one_sightings_creater_info = {
                'id' : row['users.id'],
                'first_name' : row['first_name'],
                'last_name' : row['last_name'],
                'email' : row['email'],
                'password' : row['password'],
                'created_at' : row['users.created_at'],
                'updated_at' : row['users.updated_at']
            }
            creator = User(one_sightings_creater_info)
            one_sighting.creator = creator
            all_sightings.append(one_sighting)
        return all_sightings

    @staticmethod
    def validate_sighting(sighting):
        is_valid = True
        if len(sighting['location']) < 1:
            flash('Please enter a valid location for this sighting', 'sighting')
            is_valid = False
        if len(sighting['what_happened']) < 1:
            flash('Please say what happened, or no one will believe you', 'sighting')
            is_valid = False
        if not sighting['date']:
            flash('Please say when the sighting occured', 'sighting')
            is_valid = False
        if int(sighting['number']) < 1:
            flash('Please put in the number of squatches you saw, it has to be more than 0, duh', 'sighting')
            is_valid = False
        return is_valid

