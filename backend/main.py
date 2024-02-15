from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Annotated
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
import hashlib
import os
from dotenv import load_dotenv
import jwt
import datetime
from fastapi.middleware.cors import CORSMiddleware
from routes import post, follow, user, like, reply

origins = [
    'http://localhost:5173',
    'http://localhost:8000',
]

load_dotenv()
SECRET_KEY = os.environ.get('SECRET_KEY')

ACCESS_EXP = 5 * 60
REFRESH_EXP = 30 * 60


def hash_str(input_string):
    sha256_hash = hashlib.sha256()
    sha256_hash.update(input_string.encode('utf-8'))
    return sha256_hash.hexdigest()


def generate_token(user_id, email, exp):
    payload = {
        'user_id': user_id,
        'user_email': email,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=exp)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
models.Base.metadata.create_all(bind=engine)


class RegisterBase(BaseModel):
    name: str
    email: str
    password: str
    public: bool


class LoginBase(BaseModel):
    email: str
    password: str


class TokenBase(BaseModel):
    token: str


class LogoutBase(BaseModel):
    access: str
    refresh: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

app.include_router(post.router, prefix='/posts', tags=['posts'])
app.include_router(follow.router, prefix='/follows', tags=['follows'])
app.include_router(user.router, prefix='/users', tags=['users'])
app.include_router(like.router, prefix='/likes', tags=['likes'])
app.include_router(reply.router, prefix='/replies', tags=['replies'])


@app.post('/login/')
def access_login(req_data: LoginBase, db: db_dependency):
    result = db.query(models.User).filter(models.User.email == req_data.email).first()
    if not result:
        raise HTTPException(status_code=404, detail='User not found.')
    if hash_str(req_data.password) == result.password:
        return {
            'access': generate_token(result.id, result.email, ACCESS_EXP),
            'refresh': generate_token(result.id, result.email, REFRESH_EXP),
            'user_id': result.id,
            'user_email': result.email
        }
    raise HTTPException(status_code=400, detail='Invalid credentials.')


@app.post('/register/')
def register(req_data: RegisterBase, db: db_dependency):
    result = db.query(models.User).filter(models.User.email == req_data.email).first()
    if result:
        raise HTTPException(status_code=400, detail='User with that email already exists.')
    hashed_password = hash_str(req_data.password)
    db_user = models.User(name=req_data.name, email=req_data.email, password=hashed_password, public=req_data.public)
    db.add(db_user)
    db.commit()


@app.post('/validate/')
def validate(req_data: TokenBase, db: db_dependency):
    result = db.query(models.TokenBlacklist).filter(models.TokenBlacklist.token == req_data.token).first()
    if result:
        raise HTTPException(status_code=400, detail='Invalid token.')
    try:
        payload = jwt.decode(req_data.token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.exceptions.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail='Expired token.')
    except jwt.exceptions.InvalidTokenError:
        raise HTTPException(status_code=400, detail='Invalid token.')


@app.post('/refresh/')
def refresh(req_data: TokenBase, db: db_dependency):
    try:
        payload = jwt.decode(req_data.token, SECRET_KEY, algorithms=['HS256'])
        db_token = models.TokenBlacklist(token=req_data.token)
        db.add(db_token)
        db.commit()
        return {
            'access': generate_token(payload['user_id'], payload['user_email'], ACCESS_EXP),
            'refresh': generate_token(payload['user_id'], payload['user_email'], REFRESH_EXP),
            'user_id': payload['user_id'],
            'user_email': payload['user_email']
        }
    except jwt.exceptions.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail='Expired token')
    except jwt.exceptions.InvalidTokenError:
        raise HTTPException(status_code=400, detail='Invalid token')


@app.post('/logout/')
def logout(req_data: LogoutBase, db: db_dependency):
    db_access_token = models.TokenBlacklist(token=req_data.access)
    db_refresh_token = models.TokenBlacklist(token=req_data.refresh)
    db.add(db_access_token)
    db.add(db_refresh_token)
    db.commit()
