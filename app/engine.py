from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

engine = None
SessionLocal = None

def init_db(app):
  global engine, SessionLocal
  engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
  SessionLocal = sessionmaker(bind=engine)
  Base.metadata.create_all(engine)