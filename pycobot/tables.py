# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String
from .pycobot import Base


class User(Base):
    __tablename__ = 'users'

    uid = Column(Integer, primary_key=True)
    name = Column(String(30))
    password = Column(String(60))

    def __repr__(self):
        return "<User(uid='%s', name='%s', password='%s')>" % (
                             self.uid, self.name, self.password)


class UserPriv(Base):
    __tablename__ = 'userprivs'

    tid = Column(Integer, primary_key=True)
    uid = Column(Integer)
    priv = Column(Integer)
    secmod = Column(String(30))
    secchan = Column(String(30))

    def __repr__(self):
        return "<User(uid='%s', priv='%s', sec='%s')>" % (
                             self.uid, self.priv, self.sec)
