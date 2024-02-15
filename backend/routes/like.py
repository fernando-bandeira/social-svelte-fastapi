from fastapi import APIRouter, Depends, Header
from typing import Annotated
from sqlalchemy.orm import Session
from database import SessionLocal
import models
from utils import verify_authorization
router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.get('/post/{post_id}/')
def get_likes(post_id: int, db: db_dependency, authorization: str = Header(None)):
    verify_authorization(authorization)
    db_likes = db.query(models.PostLike).filter(
        models.PostLike.post == post_id
    ).count()

    return {
        'count': db_likes
    }


@router.get('/{user_id}/{post_id}/')
def check_like(user_id: int, post_id: int, db: db_dependency, authorization: str = Header(None)):
    verify_authorization(authorization)
    db_like = db.query(models.PostLike).filter(
        models.PostLike.user == user_id,
        models.PostLike.post == post_id
    ).first()
    return {
        'like': db_like is not None
    }


@router.post('/{user_id}/{post_id}/')
def like_post(user_id: int, post_id: int, db: db_dependency, authorization: str = Header(None)):
    verify_authorization(authorization, [user_id])
    db_like = models.PostLike(user=user_id, post=post_id)
    db.add(db_like)
    db.commit()


@router.delete('/{user_id}/{post_id}/')
def remove_like(user_id: int, post_id: int, db: db_dependency, authorization: str = Header(None)):
    verify_authorization(authorization, [user_id])
    db_like = db.query(models.PostLike).filter(
        models.PostLike.user == user_id,
        models.PostLike.post == post_id
    ).first()
    if db_like:
        db.delete(db_like)
        db.commit()
