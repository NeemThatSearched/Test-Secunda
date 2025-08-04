from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import List, Optional
from app.models import Base


organization_activity_association = Table(
    'organization_activity',
    Base.metadata,
    Column('organization_id', Integer, ForeignKey('organizations.id'), primary_key=True),
    Column('activity_id', Integer, ForeignKey('activities.id'), primary_key=True)
)

organization_phone_association = Table(
    'organization_phone',
    Base.metadata,
    Column('organization_id', Integer, ForeignKey('organizations.id'), primary_key=True),
    Column('phone_id', Integer, ForeignKey('phones.id'), primary_key=True)
)


class Building(Base):
    __tablename__ = 'buildings'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    organizations: Mapped[List["Organization"]] = relationship("Organization", back_populates="building")


class Activity(Base):
    __tablename__ = 'activities'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    parent_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('activities.id'), nullable=True)
    level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    parent: Mapped[Optional["Activity"]] = relationship("Activity", remote_side=[id], back_populates="children")
    children: Mapped[List["Activity"]] = relationship("Activity", back_populates="parent")
    organizations: Mapped[List["Organization"]] = relationship(
        "Organization", 
        secondary=organization_activity_association, 
        back_populates="activities"
    )


class Phone(Base):
    __tablename__ = 'phones'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    number: Mapped[str] = mapped_column(String(20), nullable=False)

    organizations: Mapped[List["Organization"]] = relationship(
        "Organization", 
        secondary=organization_phone_association, 
        back_populates="phones"
    )


class Organization(Base):
    __tablename__ = 'organizations'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(300), nullable=False, index=True)
    building_id: Mapped[int] = mapped_column(Integer, ForeignKey('buildings.id'), nullable=False)

    building: Mapped["Building"] = relationship("Building", back_populates="organizations")
    phones: Mapped[List["Phone"]] = relationship(
        "Phone", 
        secondary=organization_phone_association, 
        back_populates="organizations"
    )
    activities: Mapped[List["Activity"]] = relationship(
        "Activity", 
        secondary=organization_activity_association, 
        back_populates="organizations"
    )