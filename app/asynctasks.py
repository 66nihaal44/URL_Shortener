from threading import Thread
from .engine import SessionLocal
from .sqlclass import URL, Click

def log_click_func(short_code):
  session = SessionLocal()
  try:
    url = session.query(URL).filter_by(short_code=short_code).first()
    if url:
      url.click_count += 1
      click = Click(url_id=url.id)
      session.add(click)
      session.commit()
  finally:
    session.close()

def log_click(short_code):
  thread = Thread(target = log_click_func, args=(short_code,))
  thread.daemon = True
  thread.start()
