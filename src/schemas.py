from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    fullname: str | None = None
    email: str
    

class UserSignup(UserCreate):
    password: str


class UserOut(UserCreate):
    id : int
    model_config = { "from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type:str


class TokenData(BaseModel):
    username: str | None = None