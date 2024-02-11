from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)
    email = Column(String, index=True, unique=True)
    password = Column(String)
    public = Column(Boolean, default=False)

    post = relationship('Post', cascade='all,delete', backref='parent')
    follow = relationship('FollowRelation', cascade='all,delete', backref='parent')
    like = relationship('PostLike', cascade='all,delete', backref='parent')
    reply = relationship('PostReply', cascade='all,delete', backref='parent')


class TokenBlacklist(Base):
    __tablename__ = 'jwt_blacklist'

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String)


class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, index=True)
    author = Column(Integer, ForeignKey('users.id'), index=True)
    content = Column(String, index=True)
    date = Column(String, index=True)
    edited = Column(Boolean)
    repost = Column(Boolean)
    reference = Column(Integer, ForeignKey('posts.id'), index=True)

    like = relationship('PostLike', cascade='all,delete', backref='parent')
    reply = relationship('PostReply', cascade='all,delete', backref='parent')


class FollowRelation(Base):
    __tablename__ = 'follows'

    id = Column(Integer, primary_key=True, index=True)
    requester = Column(Integer, ForeignKey('users.id'), index=True)
    approver = Column(Integer, ForeignKey('users.id'), index=True)
    approved = Column(Boolean, default=False)


class PostLike(Base):
    __tablename__ = 'likes'

    id = Column(Integer, primary_key=True, index=True)
    user = Column(Integer, ForeignKey('users.id'), index=True)
    post = Column(Integer, ForeignKey('posts.id'), index=True)


class PostReply(Base):
    __tablename__ = 'replies'

    id = Column(Integer, primary_key=True, index=True)
    post = Column(Integer, ForeignKey('posts.id'), index=True)
    author = Column(Integer, ForeignKey('users.id'), index=True)
    date = Column(String, index=True)
    content = Column(String, index=True)
