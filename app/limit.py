from flask_limiter import Limiter
import os

def get_client_id():
  forwarded_for = request.headers.get("X-Forwarded-For")
  if forwarded_for:
    return forwarded_for.split(",")[0].strip[]
  return request.remote_addr

limiter = Limiter(
  key_func=get_client_id,
  storage_uri=os.getenv("REDIS_URL"),
  #storage_options={"socket_connect_timeout": 30},
  strategy="fixed-window",
  default_limits=["200 per day", "50 per hour"]
)