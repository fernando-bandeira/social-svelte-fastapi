from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel
from typing import Annotated, Optional
from sqlalchemy.orm import Session
from database import SessionLocal
import models
from utils import verify_authorization, get_user_from_token, generate_post_payload
from sqlalchemy import desc, or_
router = APIRouter()


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


@router.post('/')
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


@router.put('/{post_id}/')
def edit_post(post_id: int, req_data: PostBase, db: db_dependency, authorization: str = Header(None)):
    verify_authorization(authorization, [req_data.author])
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post:
        db_post.content = req_data.content
        db_post.edited = True
        db.commit()


@router.delete('/{post_id}/')
def delete_post(post_id: int, db: db_dependency, authorization: str = Header(None)):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post:
        verify_authorization(authorization, [db_post.author])
        db.delete(db_post)
        db.commit()


@router.get('/user/{user_id}/')
def get_posts_from_user(user_id: int, db: db_dependency, authorization: str = Header(None)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user.public:
        verify_authorization(authorization, followers_of=user_id, db=db)
    else:
        verify_authorization(authorization, allow_all=True)
    db_posts = db.query(models.Post).filter(models.Post.author == user_id).order_by(desc(models.Post.id)).all()
    response_payload = []
    visiting_user = get_user_from_token(authorization)
    for post in db_posts:
        payload = generate_post_payload(post, visiting_user, db_user, db)
        response_payload.append(payload)
    return response_payload


@router.get('/feed/{user_id}/')
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
        payload = generate_post_payload(post, user_id, db_user, db)
        response_payload.append(payload)
    return response_payload
