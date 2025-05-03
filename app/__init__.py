import logging
from flask import Flask
from .database import init_db

def create_app():
    app = Flask(
        __name__,
        template_folder='templates',
        static_folder='static'
    )

    # 1) Point at the right MongoDB + DB name
    app.config['MONGO_URI'] = 'mongodb://localhost:27017/uumedi'

    # 2) Initialize and attach app.db
    init_db(app)

    # 3) Register your routes blueprint
    from .routes import main as main_bp
    app.register_blueprint(main_bp)

    # 4) Turn on DEBUG‐level logging
    logging.basicConfig(level=logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)
    app.logger.debug(f"✔️ Connected to MongoDB database: {app.db.name}")

    return app
