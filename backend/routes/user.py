from fastapi import APIRouter, Depends, Header
from typing import Annotated
from sqlalchemy.orm import Session
from database import SessionLocal
import models
from utils import verify_authorization, get_mutual_followers_qty
router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.get('/')
def search_users(name: str, db: db_dependency, authorization: str = Header(None), page: int = 1):
    user_id = verify_authorization(authorization, allow_all=True)
    PAGE_SIZE = 20
    offset = (page - 1) * PAGE_SIZE
    users = db.query(models.User).filter(
        models.User.name.ilike(f'%{name}%'),
        models.User.id != user_id
    ).offset(offset).limit(PAGE_SIZE).all()
    response_payload = []
    for user in users:
        follow_request = db.query(models.FollowRelation).filter(
            models.FollowRelation.requester == user_id,
            models.FollowRelation.approver == user.id
        ).first()
        requested = follow_request is not None
        approved = follow_request.approved if requested else False
        payload = {
            'id': user.id,
            'name': user.name,
            'public': user.public,
            'followInfo': {
                'mutual': get_mutual_followers_qty(user.id, user_id, db),
                'requested': requested,
                'approved': approved
            }
        }
        response_payload.append(payload)
    return sorted(response_payload, key=lambda u: u['followInfo']['mutual'], reverse=True)


@router.get('/{user_id}/')
def get_user_data(user_id: int, db: db_dependency, authorization: str = Header(None)):
    visiting_user = verify_authorization(authorization, allow_all=True)

    followers_count = db.query(models.FollowRelation).filter(
        models.FollowRelation.approver == user_id,
        models.FollowRelation.approved
    ).count()

    following_count = db.query(models.FollowRelation).filter(
        models.FollowRelation.requester == user_id,
        models.FollowRelation.approved
    ).count()

    mutual_count = get_mutual_followers_qty(visiting_user, user_id, db)

    follow_request = db.query(models.FollowRelation).filter(
        models.FollowRelation.requester == visiting_user,
        models.FollowRelation.approver == user_id
    ).first()
    requested = follow_request is not None
    approved = follow_request.approved if requested else False

    user = db.query(models.User).filter(models.User.id == user_id).first()
    payload = {
        'id': user.id,
        'name': user.name,
        'public': user.public,
        'followInfo': {
            'followers': followers_count,
            'following': following_count,
            'mutual': mutual_count,
            'requested': requested,
            'approved': approved
        }
    }
    return payload
