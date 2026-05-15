from flask import render_template
from urllib.parse import urlparse

def is_valid_url(url):
  parsed = urlparse(url)
  return (parsed.scheme in ("http", "https") and 
         parsed.netloc and
         "." in parsed.netloc)

# Helper for redirect_handler
def password_entry(password):
  if password:
    #sub_password = request.form.get("password")
    #if not sub_password or not check_password_hash(password, sub_password):
    return render_template("password_prompt.html"), 401
  return
