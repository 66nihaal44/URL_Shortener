from flask import Blueprint, request, redirect, jsonify
from sqlalchemy import func
from datetime import datetime, timezone, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import random
import string
import re
from . import engine
from .limit import limiter
from .sqlclass import URL, Click
from .utility import is_valid_url, password_entry
from .cache import redis_client
from .asynctasks import log_click

pattern = re.compile(r'[A-Za-z0-9_-]+')

domain_url = "https://url-shortener-g54n.onrender.com"
main = Blueprint("main", __name__)
@main.route("/shorten", methods=["POST"])
@limiter.limit("10 per minute, 100 per hour")
def shorten():
  data = request.json
  if not data or "url" not in data:
    return jsonify({"error": "Missing URL"}), 400
  if not is_valid_url(data["url"]):
    return jsonify({"error": "Invalid URL"}), 400
  original_url = data["url"]
  custom_url = data["customUrl"] if data["customUrl"] else None
  expiry_date = datetime.strptime(data["expiryDate"], '%Y-%m-%d') if data["expiryDate"] else None
  hashed_password = generate_password_hash(data["password"]) if data["password"] else None
  print("expiry_date: ", expiry_date, flush=True)
  session = engine.SessionLocal()
  try:
    exists = session.query(URL).filter_by(original_url=original_url).first()
    if exists:
      redis_client.set(exists.short_code, exists.original_url, ex=3600)
      return jsonify({
             "short_url": f"{domain_url}/{exists.short_code}"
             }), 200
    if custom_url:
      exists = session.query(URL).filter_by(short_code=custom_url).first()
      if not exists:
        if custom_url and not pattern.fullmatch(custom_url):
          return jsonify({"error": "Invalid custom URL"}), 400
        short_code = custom_url
      else:
        return jsonify({"error": "URL already exists"}), 409
    else:
      short_code = gen_random_code(session)
    url = URL(original_url=original_url, short_code = short_code)
    url.expires_at = expiry_date if expiry_date else None
    url.hashed_password = hashed_password if hashed_password else None
    session.add(url)
    session.flush()
    session.commit()
    redis_client.set(short_code, original_url, ex=3600) # redis_client here
  finally:
    session.close()
  return jsonify({
         "short_url": f"{domain_url}/{short_code}"
         }), 201
@main.route("/<short_code>")
@limiter.limit("200 per minute, 2000 per hour")
def redirect_handler(short_code):
  referrer = request.headers.get("Referer")
  cached_url = redis_client.get(short_code)
  #cached_password = redis_client.get(hashed_password)
  if cached_url:
    log_click(short_code, referrer)
    #password_entry(cached_password)
    return redirect(cached_url)
  session = engine.SessionLocal()
  try:
    url = session.query(URL).filter_by(short_code=short_code).first()
    print("DB result:", url)
    if not url:
     return jsonify({"error": "URL not found"}), 404
    if url.expires_at and url.expires_at < datetime.utcnow():
      return jsonify({"error": "Link expired"}), 410
    redis_client.set(short_code, original_url, ex=3600) # 1 hour
    log_click(short_code, referrer=None)
  finally:
    session.close()
  #password_entry(url.hashed_password)
  return redirect(url.original_url)

@main.route("/stats/<short_code>")
@limiter.limit("30 per minute, 300 per hour")
def stats(short_code):
  session = engine.SessionLocal()
  try:
    url = session.query(URL).filter_by(short_code=short_code).first()
    if not url:
      return jsonify({
             "error": "URL not found"
             }), 404
    return jsonify({
      "original_url": url.original_url,
      "short_code": short_code,
      "created_at": url.created_at,
      "age_seconds": (datetime.now(timezone.utc) - url.created_at).total_seconds(),
      "click_count": url.click_count,
      "expires_at": url.expires_at if url.expires_at else None
    })
  finally:
    session.close()

@main.route("/analytics/last-day")
def clicks_last_day():
  session = engine.SessionLocal()
  try:
    since = datetime.now(timezone.utc) - timedelta(days=1)
    count = session.query(func.count()).filter(
      Click.timestamp > since
    ).scalar()
  finally:
    session.close()
  return {"clicks_last_day": count}

@main.route("/analytics/referrers")
def clicks_referrers():
  session = engine.SessionLocal()
  try:
    results = ( session.query(Click.referrer, func.count(Click.id))
                .group_by(Click.referrer).all()
              )
    results = [tuple(row) for row in results]
  finally:
    session.close()
  return {"clicks_referrers": results}

base62 = string.ascii_letters + string.digits
def gen_random_code(session, length = 6):
  while True:
    short_code = ''.join(random.choices(base62, k=length))
    exists = session.query(URL).filter_by(short_code=short_code).first()
    if not exists:
      return short_code
