from urllib.parse import urlparse

def is_valid_url(url):
  parsed = urlparse(url)
  return (parsed.scheme in ("http", "https") and 
         parsed.netloc and
         "." in parsed.netloc)

# Helper for redirect_handler
def password_entry(url): 
  if url.hashed_password:
    sub_password = request.form.get("password")
    if not sub_password or not check_password_hash(url.hashed_password, sub_password):
      return render_template("password_prompt.html"), 401
  return
