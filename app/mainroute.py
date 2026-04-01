from flask import Blueprint, request, redirect, jsonify
from . import engine
from .sqlclass import URL, Click
from .utility import is_valid_url
from sqlalchemy import func
from datetime import datetime, timezone, timedelta
import random
import string

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
      return jsonify({
             "short_url": f"http://localhost:5000/{exists.short_code}"
             }), 200
    short_code = gen_random_code(session)
    url = URL(original_url=original_url, short_code = short_code)
    session.add(url)
    session.flush()
    session.commit()
  finally:
    session.close()
  return jsonify({
         "short_url": f"http://localhost:5000/{short_code}"
         }), 201
@main.route("/<short_code>")
def redirect_url(short_code):
  print("Redirect route hit:", short_code)
  session = engine.SessionLocal()
  try:
    url = session.query(URL).filter_by(short_code=short_code).first()
    print("DB result:", url)
    if not url:
      return jsonify({
             "error": "URL not found"
  }          }), 404
    if url.expires_at and url.expires_at < datetime.utcnow():
      return jsonify({
             "error": "Link expired"
             }), 410
    destination = url.original_url
    url.click_count += 1
    click = Click(url_id = url.id)
    session.add(click)
    session.commit()
  finally:
    session.close()
  return redirect(destination)

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
"""def encode_base62(num):
  if num == 0:
    return base62[0];
  arr = [];
  base = len(base62)
  while num:
    num, rem = divmod(num, base)
    arr.append(base62[rem])
  arr.reverse()
  return ''.join(arr)"""