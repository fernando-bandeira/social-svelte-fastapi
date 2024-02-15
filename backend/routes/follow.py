from fastapi import APIRouter, Depends, Header
from typing import Annotated
from sqlalchemy.orm import Session
from database import SessionLocal
import models
from utils import verify_authorization
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
