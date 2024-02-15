from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel
from typing import Annotated
from sqlalchemy.orm import Session
from database import SessionLocal
import models
from utils import verify_authorization
router = APIRouter()


class ReplyBase(BaseModel):
    author: int
    content: str
    date: str
    post: int


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.get('/{post_id}/')
def get_replies(post_id: int, db: db_dependency, authorization: str = Header(None)):
    verify_authorization(authorization)
    replies = db.query(models.PostReply).filter(
        models.PostReply.post == post_id
    ).all()
    response_payload = []
    for reply in replies:
        author = db.query(models.User).filter(models.User.id == reply.author).first()
        response_payload.append({
            'id': reply.id,
            'author': {
                'id': author.id,
                'name': author.name
            },
            'content': reply.content,
            'date': reply.date,
        })
    return response_payload


@router.post('/')
def reply(req_data: ReplyBase, db: db_dependency, authorization: str = Header(None)):
    verify_authorization(authorization)
    reply = models.PostReply(author=req_data.author, content=req_data.content, date=req_data.date, post=req_data.post)
    db.add(reply)
    db.commit()


@router.delete('/{reply_id}/')
def delete_reply(reply_id: int, db: db_dependency, authorization: str = Header(None)):
    verify_authorization(authorization)
    reply_db = db.query(models.PostReply).filter(models.PostReply.id == reply_id).first()
    db.delete(reply_db)
    db.commit()
