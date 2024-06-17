from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Boolean, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime
import enum


class Role(enum.Enum):
    admin = "admin"
    user = "user"


class Base(DeclarativeBase):
    ...


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    user_id = Column(String, unique=True, nullable=False)
    username = Column(String)
    role = Column(Enum(Role), default=Role.user, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class District(Base):
    __tablename__ = 'district'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)


class Street(Base):
    __tablename__ = 'street'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    district_id = Column(Integer, ForeignKey('district.id'), nullable=False)


class Part(Base):
    __tablename__ = 'part'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    is_available = Column(Boolean, default=True)


class Voice(Base):
    __tablename__ = 'voice'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    street_id = Column(Integer, ForeignKey('street.id'), nullable=False)
    part_id = Column(Integer, ForeignKey('part.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
