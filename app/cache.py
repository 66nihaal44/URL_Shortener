import redis
import os

REDIS_PORT = 6379
redis_client = redis.Redis(
  host=os.getenv("REDIS_HOST"),
  port=int(os.getenv(REDIS_PORT)),
  decode_responses=True
)
