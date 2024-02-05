from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Annotated, Optional
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session, aliased
import hashlib
import os
from dotenv import load_dotenv
import jwt
import datetime
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import desc, not_, or_, and_

origins = [
    'http://localhost:5173',
    'http://localhost:8000',
]

load_dotenv()
SECRET_KEY = os.environ.get('SECRET_KEY')

ACCESS_EXP = 30 * 60
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


def verify_authorization(token: str, authorized_users: list = []):
    try:
        if 'Bearer ' in token:
            token = token.split('Bearer ')[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        if payload['user_id'] in authorized_users or authorized_users == []:
            return payload
        raise HTTPException(status_code=403, detail='Forbidden access')
    except jwt.exceptions.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Expired token.')
    except (jwt.InvalidTokenError, ValueError):
        raise HTTPException(status_code=401, detail='Invalid token.')
    except Exception:
        raise HTTPException(status_code=401, detail='Forbidden access')


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


class PostBase(BaseModel):
    author: int
    content: str
    date: str
    repost: bool
    reference: Optional[int]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


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


@app.post('/create-post/')
def create_post(req_data: PostBase, db: db_dependency, authorization: str = Header(None)):
    verify_authorization(authorization, [req_data.author])
    db_post = models.Post(
        author=req_data.author,
        content=req_data.content,
        date=req_data.date,
        edited=False,
        repost=req_data.repost,
        reference=req_data.reference
    )
    db.add(db_post)
    db.commit()


@app.put('/edit-post/{post_id}/')
def edit_post(post_id: int, req_data: PostBase, db: db_dependency, authorization: str = Header(None)):
    verify_authorization(authorization, [req_data.author])
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post:
        db_post.content = req_data.content
        db_post.edited = True
        db.commit()


@app.delete('/delete-post/{post_id}/')
def delete_post(post_id: int, db: db_dependency, authorization: str = Header(None)):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post:
        verify_authorization(authorization, [db_post.author])
        db.delete(db_post)
        db.commit()


@app.get('/post/{post_id}/')
def get_post(post_id: int, db: db_dependency, authorization: str = Header(None)):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    db_user = db.query(models.User).filter(models.User.id == db_post.author).first()
    verify_authorization(authorization)
    return {
        'id': db_post.id,
        'author': {
            'id': db_user.id,
            'name': db_user.name,
        },
        'content': db_post.content,
        'date': db_post.date,
        'edited': db_post.edited,
        'repost': db_post.repost,
        'reference': db_post.reference
    }


@app.get('/posts/{user_id}/')
def get_posts_from_user(user_id: int, db: db_dependency, authorization: str = Header(None)):
    verify_authorization(authorization)
    db_posts = db.query(models.Post).filter(models.Post.author == user_id).order_by(desc(models.Post.id)).all()
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    response_payload = [{
        'id': post.id,
        'author': {
            'id': db_user.id,
            'name': db_user.name,
        },
        'content': post.content,
        'date': post.date,
        'edited': post.edited,
        'repost': post.repost,
        'reference': post.reference
    } for post in db_posts]
    return response_payload


@app.get('/users/')
def search_users(name: str, db: db_dependency, authorization: str = Header(None)):
    payload = verify_authorization(authorization)
    users = db.query(models.User).filter(
        models.User.name.contains(name),
        models.User.id != payload['user_id']
    ).all()
    return users


@app.get('/user/{user_id}/')
def get_user_data(user_id: int, db: db_dependency, authorization: str = Header(None)):
    verify_authorization(authorization)
    user = db.query(models.User).filter(models.User.id == user_id).first()
    return user


@app.get('/{user_1}/follows/{user_2}/')
def check_relation(user_1: int, user_2: int, db: db_dependency, authorization: str = Header(None)):
    verify_authorization(authorization, [user_1, user_2])
    result = db.query(models.FollowRelation).filter(
        models.FollowRelation.requester == user_1,
        models.FollowRelation.approver == user_2
    ).first()
    requested = result is not None
    approved = result.approved if requested else False
    return {
        'requested': requested,
        'approved': approved
    }


@app.post('/{user_1}/follows/{user_2}/')
def follow(user_1: int, user_2: int, db: db_dependency, authorization: str = Header(None)):
    verify_authorization(authorization, [user_1])
    db_approver = db.query(models.User).filter(models.User.id == user_2).first()
    db_follow = models.FollowRelation(requester=user_1, approver=user_2, approved=db_approver.public)
    db.add(db_follow)
    db.commit()


@app.delete('/{user_1}/follows/{user_2}/')
def unfollow(user_1: int, user_2: int, db: db_dependency, authorization: str = Header(None)):
    verify_authorization(authorization, [user_1, user_2])
    result = db.query(models.FollowRelation).filter(
        models.FollowRelation.requester == user_1,
        models.FollowRelation.approver == user_2
    ).first()
    if result:
        db.delete(result)
        db.commit()


@app.put('/{user_1}/approves/{user_2}/')
def approve(user_1: int, user_2: int, db: db_dependency, authorization: str = Header(None)):
    verify_authorization(authorization, [user_1])
    db_relation = db.query(models.FollowRelation).filter(
        models.FollowRelation.approver == user_1,
        models.FollowRelation.requester == user_2
    ).first()
    if db_relation:
        db_relation.approved = True
        db.commit()


@app.get('/requests/{user_id}/')
def get_requests(user_id: int, db: db_dependency, authorization: str = Header(None)):
    verify_authorization(authorization, [user_id])
    db_requests = db.query(models.FollowRelation).filter(
        models.FollowRelation.approver == user_id,
        not_(models.FollowRelation.approved)
    ).all()
    response_payload = []
    for request in db_requests:
        requester_name = db.query(models.User).filter(models.User.id == request.requester).first().name
        response_payload.append({
            'id': request.id,
            'requester': request.requester,
            'requester_name': requester_name
        })
    return response_payload


@app.get('/{user_id}/likes/{post_id}/')
def check_like(user_id: int, post_id: int, db: db_dependency, authorization: str = Header(None)):
    verify_authorization(authorization)
    db_like = db.query(models.PostLike).filter(
        models.PostLike.user == user_id,
        models.PostLike.post == post_id
    ).first()
    return {
        'like': db_like is not None
    }


@app.post('/{user_id}/likes/{post_id}/')
def like_post(user_id: int, post_id: int, db: db_dependency, authorization: str = Header(None)):
    verify_authorization(authorization, [user_id])
    db_like = models.PostLike(user=user_id, post=post_id)
    db.add(db_like)
    db.commit()


@app.delete('/{user_id}/likes/{post_id}/')
def remove_like(user_id: int, post_id: int, db: db_dependency, authorization: str = Header(None)):
    verify_authorization(authorization, [user_id])
    db_like = db.query(models.PostLike).filter(
        models.PostLike.user == user_id,
        models.PostLike.post == post_id
    ).first()
    if db_like:
        db.delete(db_like)
        db.commit()


@app.get('/feed/{user_id}')
def get_feed_posts(user_id: int, db: db_dependency, authorization: str = Header(None)):
    verify_authorization(authorization, [user_id])
    followed_users_posts = db.query(models.Post).join(
        models.FollowRelation,
        or_(
            models.Post.author == models.FollowRelation.approver,
            models.Post.author == user_id
        )
    ).filter(
        models.FollowRelation.requester == user_id,
        models.FollowRelation.approved
    ).order_by(desc(models.Post.date)).all()

    response_payload = []
    for post in followed_users_posts:
        db_user = db.query(models.User).filter(models.User.id == post.author).first()
        response_payload.append({
            'id': post.id,
            'author': {
                'id': db_user.id,
                'name': db_user.name,
            },
            'content': post.content,
            'date': post.date,
            'edited': post.edited,
            'repost': post.repost,
            'reference': post.reference
        })

    return response_payload


@app.get('/profile-info/{user_id}/{profile_id}/')
def get_followers_qty(user_id: int, profile_id: int, db: db_dependency, authorization: str = Header(None)):
    verify_authorization(authorization, [user_id])

    db_followers = db.query(models.FollowRelation).filter(
        models.FollowRelation.approver == profile_id,
        models.FollowRelation.approved
    ).count()

    db_following = db.query(models.FollowRelation).filter(
        models.FollowRelation.requester == profile_id,
        models.FollowRelation.approved
    ).count()

    f1 = aliased(models.FollowRelation)
    f2 = aliased(models.FollowRelation)

    db_mutual = db.query(f1).join(f2, f1.requester == f2.requester).filter(
        f1.approved,
        f2.approved,
        or_(
            and_(f1.approver == user_id, f2.approver == profile_id),
            and_(f1.approver == profile_id, f2.approver == user_id),
        )
    ).distinct().count()

    return {
        'followers': db_followers,
        'following': db_following,
        'mutual': db_mutual / 2
    }


@app.get('/likes/{post_id}/')
def get_likes(post_id: int, db: db_dependency, authorization: str = Header(None)):
    verify_authorization(authorization)
    db_likes = db.query(models.PostLike).filter(
        models.PostLike.post == post_id
    ).count()

    return {
        'count': db_likes
    }
