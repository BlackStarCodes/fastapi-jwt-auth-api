from dotenv import dotenv_values

v = dotenv_values(".env")

SECRET_KEY= v["SECRET_KEY"]
ALGO = v["ALGORITHM"]
TOKEN_EXPIRE_MINS = 30

url = v["DATABASE_url"]