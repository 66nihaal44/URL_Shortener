import string

base62 = string.digits + string.ascii_letters

def encode_base62(num):
  if num == 0:
    return base62[0];
  arr = [];
  base = len(base62)
  while num:
    num, rem = divmod(num, base)
    arr.append(base62[rem])
  arr.reverse()
  return ' '.join(arr)