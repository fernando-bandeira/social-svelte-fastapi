import models
import jwt
import re
import os
from fastapi import HTTPException, Depends
from dotenv import load_dotenv
from sqlalchemy import or_, and_
from sqlalchemy.orm import aliased, Session
from typing import Optional, Annotated
from database import SessionLocal

load_dotenv()
SECRET_KEY = os.environ.get('SECRET_KEY')


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


def get_user_from_token(token: str):
    try:
        if 'Bearer ' in token:
            token = token.split('Bearer ')[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['user_id']
    except jwt.exceptions.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Expired token.')
    except (jwt.InvalidTokenError, ValueError):
        raise HTTPException(status_code=401, detail='Invalid token.')
    except Exception:
        raise HTTPException(status_code=401, detail='Forbidden access')


def verify_authorization(
    token: str,
    authorized_users: list = [],
    followers_of: int = 0,
    db: Optional[db_dependency] = None,
    allow_all: bool = False
):
    user_id = get_user_from_token(token)
    if followers_of and db:
        followers = db.query(models.FollowRelation.requester).filter(
            models.FollowRelation.approver == followers_of,
            models.FollowRelation.approved
        ).all()
        authorized_followers = [follower[0] for follower in followers]
        authorized_followers.append(followers_of)
    else:
        authorized_followers = []
    authorized_users.extend(authorized_followers)

    if user_id in authorized_users or allow_all:
        return user_id
    raise HTTPException(status_code=403, detail='Forbidden access')


def get_tags(content, db):
    pattern = r'@([^@]+)@'
    matches = re.findall(pattern, content)
    tags = []
    for match in matches:
        try:
            match = int(match)
            tagged_user = db.query(models.User).filter(models.User.id == match).first()
            if tagged_user:
                tags.append({
                    'id': tagged_user.id,
                    'name': tagged_user.name
                })
            else:
                tags.append(match)
        except ValueError:
            tags.append(match)
    return tags


def generate_post_payload(post, user_id, author, db):
    if post.repost:
        original_post = db.query(models.Post).filter(
            models.Post.id == post.reference
        ).first()
        content = original_post.content
    else:
        content = post.content
    tags = get_tags(content, db)

    like_count = db.query(models.PostLike).filter(models.PostLike.post == post.id).count()
    liked = db.query(models.PostLike).filter(
        models.PostLike.post == post.id,
        models.PostLike.user == user_id
    ).first()

    repost_count = db.query(models.Post).filter(models.Post.reference == post.id).count()

    reply_count = db.query(models.PostReply).filter(models.PostReply.post == post.id).count()

    payload = {
        'id': post.id,
        'author': {
            'id': author.id,
            'name': author.name,
        },
        'content': content,
        'date': post.date,
        'edited': post.edited,
        'repost': post.repost,
        'tags': tags,
        'likeCount': like_count,
        'liked': bool(liked),
        'repostCount': repost_count,
        'replyCount': reply_count
    }
    if post.repost:
        original_author = db.query(models.User).filter(models.User.id == original_post.author).first()
        payload['author']['original'] = {
            'id': original_author.id,
            'name': original_author.name
        }
    return payload


def get_mutual_followers_qty(user1, user2, db):
    f1 = aliased(models.FollowRelation)
    f2 = aliased(models.FollowRelation)
    mutual_count = db.query(f1.requester).join(f2, f1.requester == f2.requester).filter(
        f1.approved,
        f2.approved,
        or_(
            and_(f1.approver == user1, f2.approver == user2),
            and_(f1.approver == user2, f2.approver == user1),
        )
    ).distinct().count()

    return mutual_count
