# -*- coding: utf-8 -*-
from farmsList.database import (
    Column,
    Table,
    db,
    Model,
    ReferenceCol,
    relationship,
    SurrogatePK,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

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
    apn = Column(db.BigInteger(), nullable=False, unique=True)
    landType = Column(db.String(80), nullable=True)

    def __init__(self, **kwargs):
        db.Model.__init__(self, **kwargs)

    def __repr__(self):
        return '<Parcel({id})>'.format(id=self.id)

class Farmland(SurrogatePK, Model):
    __tablename__ = 'farmlands'
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
    landType = Column(db.String(80), nullable=True)

    def __init__(self, **kwargs):
        db.Model.__init__(self, **kwargs)

    def __repr__(self):
        return '<Farmland({id})>'.format(id=self.id)

association_table = Table('parcel-farmland', Base.metadata,
    Column('parcel_apn', db.BigInteger(), db.ForeignKey('parcels.apn')),
    Column('farmland_id', db.Integer(), db.ForeignKey('farmlands.id'))
)

class AdditionalLayer(SurrogatePK, Model):
    __tablename__ = 'additional_layers'
    name = Column(db.String(400), nullable=False)
    geometry = Column(db.String(6250000), nullable=False)

    def __init__(self, **kwargs):
        db.Model.__init__(self, **kwargs)

    def __repr__(self):
        return '<AdditionalLayer({id}, {name})>'.format(id=self.id, name=self.name)
