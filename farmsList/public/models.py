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
from geoalchemy2.types import Geometry

Base = declarative_base()

class Parcel(SurrogatePK, Model):
    __tablename__ = 'parcels'
    size = Column(db.Numeric(precision=6, scale=2), nullable = False)
    water = Column(db.Numeric(precision=3, scale=0), nullable=True)
    soil = Column(db.String(400), nullable=True)
    zoning = Column(db.String(80), nullable=False)
    geometry = Column(db.String(6250000), nullable=False)
    center = Column(db.String(2000), nullable=False)
    geom = Column(Geometry(geometry_type='MULTIPOLYGON'))
    cent = Column(Geometry(geometry_type='POINT'))
    developmentPlan = Column(db.String(400), nullable=True)
    restrictions = Column(db.String(400), nullable=True)
    address = Column(db.String(400), nullable=True)
    apn = Column(db.BigInteger(), nullable=False, unique=True)
    jurisdiction = Column(db.String(400))
    landType = Column(db.String(80), nullable=True)
    landUse = Column(db.String(80), nullable=True)

    def __init__(self, **kwargs):
        db.Model.__init__(self, **kwargs)

    def __repr__(self):
        return '<Parcel({id})>'.format(id=self.id)

class Farmland(SurrogatePK, Model):
    __tablename__ = 'farmlands'
    size = Column(db.Numeric(precision=6, scale=2), nullable = False)
    hasWater = Column(db.Boolean(), nullable=False, server_default='False')
    water = Column(db.Numeric(precision=3, scale=0), nullable=True)
    public = Column(db.Boolean(), nullable=False, server_default='False')
    soil = Column(db.String(400), nullable=True)
    zoning = Column(db.String(80), nullable=False)
    geometry = Column(Geometry(geometry_type='MULTIPOLYGON'), nullable=False)
    center = Column(Geometry(geometry_type='POINT'), nullable=False)
    developmentPlan = Column(db.String(400), nullable=True)
    ownerName = Column(db.String(400), nullable=True)
    address = Column(db.String(400), nullable=True)
    email = Column(db.String(80), nullable=True)
    monthlyCost = Column(db.Numeric(precision=7, scale=2), nullable = False)
    priorUses = Column(db.String(10000), nullable=True)

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
    geom = Column(Geometry(geometry_type='MULTIPOLYGON'), nullable=False)

    def __init__(self, **kwargs):
        db.Model.__init__(self, **kwargs)

    def __repr__(self):
        return '<AdditionalLayer({id}, {name})>'.format(id=self.id, name=self.name)

class RemoteDataset(SurrogatePK, Model):
    __tablename__ = 'remote_datasets'
    name = Column(db.String(400), nullable=False)
    url = Column(db.String(2000), nullable=False)
    lastUpdatedLocally = Column(db.DateTime, nullable=False, default=0)

    def __init__(self, **kwargs):
        db.Model.__init__(self, **kwargs)

    def __repr__(self):
        return '<RemoteDataset({name})>'.format(name=self.name)
