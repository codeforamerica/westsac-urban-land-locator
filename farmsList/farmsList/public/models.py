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
    size = Column(db.Numeric(precision=4, scale=2), nullable = False)
    water = Column(db.Boolean(), default=False)
    zoning = Column(db.String(80), nullable=False)
    developmentPlan = Column(db.String(400), nullable=True)
    restrictions = Column(db.String(400), nullable=True)
    image = Column(db.String(400), nullable=True)
    address = Column(db.String(400), nullable=True)
    email = Column(db.String(80), nullable=True)

    def __init__(self, name, **kwargs):
        db.Model.__init__(self, name=name, **kwargs)

    def __repr__(self):
        return '<Parcel({name})>'.format(name=self.name)
