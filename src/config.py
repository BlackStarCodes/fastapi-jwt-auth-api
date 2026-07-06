from dotenv import dotenv_values

v = dotenv_values(".env")

SECRET_KEY= v["SECRET_KEY"]
ALGO = v["ALGORITHM"]
TOKEN_EXPIRE_MINS = 30

user = v["user"]
pin = v["pin"]
host = v["host"]
port = v["port"]
db_name = v["db_name"]