from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"


def create_access_token(data: dict , time:float):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=time)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def auth_token(token: str = Depends(oauth2_scheme)):
    try:
            payload = jwt.decode(token,SECRET_KEY, ALGORITHM)
            return {'Value': True , 'Message':"Signed token" , 'id': payload['id'],'role':payload['role']}
    except JWTError:
            return {'Value': False , 'Message':"Unauthorized token"}
    

