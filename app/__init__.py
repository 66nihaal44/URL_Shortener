from flask import Flask
from flask_cors import CORS
from .engine import init_db
from .mainroute import main
import os
from flask_limiter import Limiter

def get_client_id():
  forwarded_for = request.headers.get("X-Forwarded-For")
  if forwarded_for:
    return forwarded_for.split(",")[0].strip()
  return request.remote_addr

limiter = Limiter(
  key_func=get_client_id,
  storage_uri=os.getenv("REDIS_URL"),
  strategy="fixed-window",
  default_limits=["200 per day", "50 per hour"]
)

def create_app():
  app = Flask(__name__)
  app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
  limiter.init_app(app)
  init_db(app)
  app.register_blueprint(main)
  CORS(app)
  print(app.url_map)
  return app
