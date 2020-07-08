#!/usr/bin/python3

from sqlalchemy import Column, Integer, String, Date, Text
from sqlalchemy.ext.declarative import declarative_base

# 创建对象的基类:
Base = declarative_base()

class Corp(Base):
    __tablename__ = "corporations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    letter = Column(String)
    ceref = Column(String(10), unique=True)
    typeID = Column(Integer, default=0)
    typeName = Column(String(100))
    typeNameChi = Column(String(100))
    name = Column(String(255))
    nameChi = Column(String(255))
    address = Column(String(1000))
    addressChi = Column(String(1000))
    licence_date = Column(Date)
    remarks = Column(String(1000))
    email = Column(String(255))
    website = Column(String(255))


class CorpActions(Base):
    __tablename__ = "corporations_actions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ceref = Column(String(10))
    action_date = Column(Date)
    action_name = Column(String(255))
    en = Column(String(255))
    cn = Column(String(255))


class CorpCo(Base):
    __tablename__ = "corporations_complaints_officers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ceref = Column(String(10))
    tel = Column(String(255))
    fax = Column(String(255))
    email = Column(String(255))
    address = Column(String(1000))
    addressChi = Column(String(1000))


class CorpConditions(Base):
    __tablename__ = "corporations_conditions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ceref = Column(String(10))
    effective_date = Column(Date)
    condition = Column(Text)
    conditionChi = Column(Text)
    applNo = Column(String(255))
    lcSeqNo = Column(String(255))


class CorpDetails(Base):
    __tablename__ = "corporations_details"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ceref = Column(String(10))
    name = Column(String(255))
    nameChi = Column(String(255))
    effDate = Column(Date)
    endDate = Column(Date)
    remarks = Column(String(1000))


class CorpLicences(Base):
    __tablename__ = "corporations_licences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ceref = Column(String(10))
    licence_type = Column(String(10))
    licence_type_name = Column(String(255))
    actType = Column(String(255))
    actDesc = Column(String(255))
    actDescChi = Column(String(255))
    actStatus = Column(String(255))
    effDate = Column(Date)
    endDate = Column(Date)


class CorpPrevName(Base):
    __tablename__ = "corporations_previous"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ceref = Column(String(10))
    changeDate = Column(Date)
    englishName = Column(String(255))
    chineseName = Column(String(255))
    surname = Column(String(255))
    otherName = Column(String(255))

class CorpRep(Base):
    __tablename__ = "corporations_rep"

    id = Column(Integer, primary_key=True, autoincrement=True)
    corp = Column(String(10))
    indi = Column(String(10))


class CorpConditions(Base):
    __tablename__ = "corporations_ro"

    id = Column(Integer, primary_key=True, autoincrement=True)
    corp = Column(String(10))
    indi = Column(String(10))

class Indi(Base):
    __tablename__ = "individuals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    corp = Column(String(10))
    ceref = Column(String(10), unique=True)
    name = Column(String(255))
    nameChi = Column(String(255))
    licence_date = Column(Date)
    activities = Column(String(255))
    remarks = Column(String(255))
