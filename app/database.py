from pymongo import MongoClient

mongo_client = None

def init_db(app):
    global mongo_client
    mongo_client = MongoClient(app.config['MONGO_URI'])
    # Attach the database object to the app
    app.db = mongo_client.get_default_database()
