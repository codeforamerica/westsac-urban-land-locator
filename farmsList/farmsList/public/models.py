# -*- coding: utf-8 -*-
from farmsList.database import (
    Column,
    db,
    Model,
    ReferenceCol,
    relationship,
    SurrogatePK,
)


class Parcel(SurrogatePK, Model):
    __tablename__ = 'parcels'
    name = Column(db.String(80), unique=True, nullable=False)

    def __init__(self, name, **kwargs):
        db.Model.__init__(self, name=name, **kwargs)

    def __repr__(self):
        return '<Role({name})>'.format(name=self.name)
