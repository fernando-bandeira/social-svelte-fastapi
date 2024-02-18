from fastapi import APIRouter, Depends, Header
from typing import Annotated
from sqlalchemy.orm import Session
from database import SessionLocal
import models
from utils import verify_authorization, get_mutual_followers_qty
from sqlalchemy import not_
router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.post('/{requester}/{approver}/')
def follow(requester: int, approver: int, db: db_dependency, authorization: str = Header(None)):
    verify_authorization(authorization, [requester])
    db_approver = db.query(models.User).filter(models.User.id == approver).first()
    db_follow = models.FollowRelation(requester=requester, approver=approver, approved=db_approver.public)
    db.add(db_follow)
    db.commit()


@router.delete('/{requester}/{approver}/')
def unfollow(requester: int, approver: int, db: db_dependency, authorization: str = Header(None)):
    verify_authorization(authorization, [requester, approver])
    result = db.query(models.FollowRelation).filter(
        models.FollowRelation.requester == requester,
        models.FollowRelation.approver == approver
    ).first()
    if result:
        db.delete(result)
        db.commit()


@router.put('/{requester}/{approver}/')
def approve(requester: int, approver: int, db: db_dependency, authorization: str = Header(None)):
    verify_authorization(authorization, [approver])
    db_relation = db.query(models.FollowRelation).filter(
        models.FollowRelation.approver == approver,
        models.FollowRelation.requester == requester
    ).first()
    if db_relation:
        db_relation.approved = True
        db.commit()


@router.get('/requests/{user_id}/')
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


@router.get('/followers/{user_id}/')
def get_followers(user_id: int, db: db_dependency, authorization: str = Header(None)):
    visiting_user = verify_authorization(authorization)
    followers = db.query(models.FollowRelation).filter(
        models.FollowRelation.approver == user_id,
        models.FollowRelation.approved,
    ).all()

    response_payload = []
    for follow_request in followers:
        requester = db.query(models.User).filter(
            models.User.id == follow_request.requester
        ).first()
        response_payload.append({
            'id': requester.id,
            'name': requester.name,
            'mutual': get_mutual_followers_qty(requester.id, visiting_user, db)
        })

    return response_payload


@router.get('/following/{user_id}/')
def get_following(user_id: int, db: db_dependency, authorization: str = Header(None)):
    visiting_user = verify_authorization(authorization)
    following = db.query(models.FollowRelation).filter(
        models.FollowRelation.requester == user_id,
        models.FollowRelation.approved,
    ).all()

    response_payload = []
    for follow_request in following:
        approver = db.query(models.User).filter(
            models.User.id == follow_request.approver
        ).first()
        response_payload.append({
            'id': approver.id,
            'name': approver.name,
            'mutual': get_mutual_followers_qty(approver.id, visiting_user, db)
        })

    return response_payload
