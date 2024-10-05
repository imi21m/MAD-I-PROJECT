
# app.py
from flask import Flask

from flask_migrate import Migrate
from config import Config
from backend.models import *


app = None  # initially none 
migrate = Migrate()

def create_app(config_class=Config):
    iescp_app = Flask(__name__)
    iescp_app.debug = True
    iescp_app.config.from_object(config_class)
    iescp_app.app_context().push()  # Direct access app by other modules(db , authentication)
    db.init_app(iescp_app)
    migrate.init_app(iescp_app, db)
    print("IESCP application started...")

    return iescp_app

app = create_app()

from backend.routes import *

if __name__ == '__main__':
    app.run(debug=True)

