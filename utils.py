from jose import jwt
from datetime import timedelta
from typing import Optional
from datetime import datetime
from settings import SECRET_KEY
import hashlib
import secrets
from elastic_search import ElaseticQuery
from fastapi import Request

es = ElaseticQuery()

ALGORITHM = "HS256"


def user_password_validation(password):
    """
    Password Validation

    Developer : Gnaneswaran.R.D

    """
    if len(password) < 8:
        return "The password must have more than 8 characters"

    # Check for at least one uppercase letter
    if not any(char.isupper() for char in password):
        return "The password must contain at least one uppercase letter"

    # Check for at least one lowercase letter
    if not any(char.islower() for char in password):
        return "The password must contain at least one lower letter"

    # Check for at least one digit
    if not any(char.isdigit() for char in password):
        return "The password must contain at least one digit"

    # Check for at least one special character
    special_characters = "!@#$%^&*()-_+=[]{}|:;<>,.?/~"
    if not any(char in special_characters for char in password):
        return "The password must contain at least one special character"

    return True


def jwt_encode(data, secret_key, algorithm="HS256"):
    """
    Encrypt the data using jwt library.

    Developer: Gnaneswaran.R.D
    """
    encoded_token = jwt.encode(data, secret_key, algorithm)
    return encoded_token


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def random_hashkey():
    """
    This function 20 character hash key

    Developer : Gnaneswaran R D
    """
    random_bytes = secrets.token_bytes(20)
    random_hex = random_bytes.hex()
    hash_key = hashlib.sha1(random_hex.encode()).hexdigest()
    return hash_key


async def get_current_user(request:Request):
    
    user_id = request.session.get("user_id")
    print("user_id--------------------",user_id)
    print("type",type(user_id))
    if user_id is not None:
        query = {
            "query" : {
                "match" : {
                    "_id" : int(user_id)
                }
            }
        }
        
        data = es.get_all_data(index="user",body=query)
        if data:
            data = data[0]
        return data
    else:
        return {"user":"none"}
    
