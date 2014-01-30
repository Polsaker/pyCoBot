# -*- coding: utf-8 -*-

from .pycobot import BaseModel
from peewee.peewee import CharField, IntegerField


class User(BaseModel):
    uid = IntegerField(primary_key=True)
    name = CharField()
    password = CharField()

    class Meta:
        db_table = "users"


class UserPriv(BaseModel):
    tid = IntegerField(primary_key=True)
    uid = IntegerField()
    priv = IntegerField()
    secmod = CharField()
    secchan = CharField()

    class Meta:
        db_table = "userprivs"