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
    listedToAdmin = Column(db.Boolean(), nullable=False, server_default='False')
    listedToPublic = Column(db.Boolean(), nullable=False, server_default='False')
    size = Column(db.Numeric(precision=6, scale=2), nullable = False)
    water = Column(db.Numeric(precision=3, scale=0), nullable=True)
    soil = Column(db.String(400), nullable=True)
    zoning = Column(db.String(80), nullable=False)
    geometry = Column(db.String(6250000), nullable=False)
    center = Column(db.String(2000), nullable=False)
    developmentPlan = Column(db.String(400), nullable=True)
    restrictions = Column(db.String(400), nullable=True)
    address = Column(db.String(400), nullable=True)
    email = Column(db.String(80), nullable=True)

    def __init__(self, **kwargs):
        db.Model.__init__(self, **kwargs)

    def __repr__(self):
        return '<Parcel({id})>'.format(id=self.id)
