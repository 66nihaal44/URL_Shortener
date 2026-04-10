from flask import Blueprint, request, redirect, jsonify
from . import engine
from .sqlclass import URL, Click
from .utility import is_valid_url
from sqlalchemy import func
from cache import redis_client
from datetime import datetime, timezone, timedelta
import random
import string

domain_url = "https://url-shortener-g54n.onrender.com"
main = Blueprint("main", __name__)
@main.route("/shorten", methods=["POST"])
def shorten():
  data = request.json
  if not data or "url" not in data:
    return jsonify({"error": "Missing URL"}), 400
  if not is_valid_url(data["url"]):
    return jsonify({"error": "Invalid URL"}), 400
  original_url = data["url"]
  session = engine.SessionLocal()
  try:
    exists = session.query(URL).filter_by(original_url=original_url).first()
    if exists:
      redis_client.set(short_code, original_url, ex=3600)
      return jsonify({
             "short_url": f"{domain_url}/{exists.short_code}"
             }), 200
    short_code = gen_random_code(session)
    url = URL(original_url=original_url, short_code = short_code)
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
def redirect_handler(short_code):
  cached_url = redis_client.get(short_code)
  if cached_url:
    url.click_count += 1
    click = Click(url_id = url.id)
    return redirect(cached_url)
  url = session.query(URL).filter_by(short_code=short_code).first()
  print("DB result:", url)
  if not url:
   return jsonify({
          "error": "URL not found"
          }), 404
  url.click_count += 1
  click = Click(url_id = url.id)
  redis_client.set(short_code, url.original_url, ex = 3600) # 1 hour
  return redirect(url.original_url)

@main.route("/stats/<short_code>")
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

base62 = string.ascii_letters + string.digits
def gen_random_code(session, length = 6):
  while True:
    short_code = ''.join(random.choices(base62, k=length))
    exists = session.query(URL).filter_by(short_code=short_code).first()
    if not exists:
      return short_code
