# -*- coding: utf-8 -*-
from .peewee import peewee

obj = peewee.SqliteDatabase('db/cobot.db', threadlocals=True)

class BaseModel(peewee.Model):
    class Meta:
        database = obj

class User(BaseModel):
    username = peewee.CharField(unique=True)
    password = peewee.CharField() # password (sha256)

class UserPriv(BaseModel):
    uid = peewee.IntegerField() # User ID (from the User table)
    priv = peewee.IntegerField() # 1-10 (privs)
    module = peewee.CharField()
    channel = peewee.CharField()
    
class Settings(BaseModel):
    type = peewee.CharField()  # Global/Network/Channel
    channel = peewee.CharField()  # Only if it is a channel setting
    network = peewee.CharField()  # Only if it is not a global setting
    name = peewee.CharField()
    value = peewee.CharField()
