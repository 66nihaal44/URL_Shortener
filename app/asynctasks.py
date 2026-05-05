from threading import Thread
from . import engine
from .sqlclass import URL, Click

def log_click_func(short_code, referrer=None):
  session = engine.SessionLocal()
  try:
    url = session.query(URL).filter_by(short_code=short_code).first()
    if url:
      url.click_count += 1
      click = Click(url_id=url.id, referrer = referrer)
      session.add(click)
      session.commit()
  finally:
    session.close()

def log_click(short_code, referrer):
  thread = Thread(target = log_click_func, args=(short_code, referrer))
  thread.daemon = True
  thread.start()
