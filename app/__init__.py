from flask import Flask
from flask_cors import CORS
from .engine import init_db
from .mainroute import main
import os

def create_app():
  app = Flask(__name__)
  app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
  init_db(app)
  app.register_blueprint(main)
  CORS(app)
  print(app.url_map)
  return app