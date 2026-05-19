from urllib.parse import urlparse
from werkzeug.security import check_password_hash

def is_valid_url(url):
  parsed = urlparse(url)
  return (parsed.scheme in ("http", "https") and 
         parsed.netloc and
         "." in parsed.netloc)

# Helper for redirect_handler
def password_check(password, sub_password):
  if not sub_password:
    return check_password_hash(password, sub_password)
