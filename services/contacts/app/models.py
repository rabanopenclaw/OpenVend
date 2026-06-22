from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Table, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def new_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(UTC)


contact_tags = Table(
    "contact_tags",
    Base.metadata,
    Column("contact_id", ForeignKey("contacts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    contact_type: Mapped[str] = mapped_column(String(32), default="person", index=True)
    display_name: Mapped[str] = mapped_column(String(160), index=True)
    organization_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    given_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    family_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="active", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )

    addresses: Mapped[list[Address]] = relationship(
        back_populates="contact",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    communication_channels: Mapped[list[CommunicationChannel]] = relationship(
        back_populates="contact",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    activities: Mapped[list[Activity]] = relationship(
        back_populates="contact",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    tags: Mapped[list[Tag]] = relationship(secondary=contact_tags, back_populates="contacts")
    organization_memberships: Mapped[list[OrganizationMembership]] = relationship(
        foreign_keys="OrganizationMembership.organization_contact_id",
        back_populates="organization_contact",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    member_memberships: Mapped[list[OrganizationMembership]] = relationship(
        foreign_keys="OrganizationMembership.member_contact_id",
        back_populates="member_contact",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Address(Base):
    __tablename__ = "addresses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    contact_id: Mapped[str] = mapped_column(
        ForeignKey("contacts.id", ondelete="CASCADE"), index=True
    )
    label: Mapped[str] = mapped_column(String(80), default="main")
    line1: Mapped[str] = mapped_column(String(160))
    line2: Mapped[str | None] = mapped_column(String(160), nullable=True)
    city: Mapped[str] = mapped_column(String(120))
    region: Mapped[str | None] = mapped_column(String(120), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(40), nullable=True)
    country_code: Mapped[str] = mapped_column(String(2))
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )

    contact: Mapped[Contact] = relationship(back_populates="addresses")


class CommunicationChannel(Base):
    __tablename__ = "communication_channels"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    contact_id: Mapped[str] = mapped_column(
        ForeignKey("contacts.id", ondelete="CASCADE"), index=True
    )
    channel_type: Mapped[str] = mapped_column(String(40))
    value: Mapped[str] = mapped_column(String(200))
    label: Mapped[str | None] = mapped_column(String(80), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )

    contact: Mapped[Contact] = relationship(back_populates="communication_channels")


class Tag(Base):
    __tablename__ = "tags"
    __table_args__ = (UniqueConstraint("name", name="uq_tags_name"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    color: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )

    contacts: Mapped[list[Contact]] = relationship(secondary=contact_tags, back_populates="tags")


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    contact_id: Mapped[str] = mapped_column(
        ForeignKey("contacts.id", ondelete="CASCADE"), index=True
    )
    activity_type: Mapped[str] = mapped_column(String(40), default="note")
    body: Mapped[str] = mapped_column(Text)
    created_by: Mapped[str] = mapped_column(String(120), default="unknown")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )

    contact: Mapped[Contact] = relationship(back_populates="activities")


class OrganizationMembership(Base):
    __tablename__ = "organization_memberships"
    __table_args__ = (
        UniqueConstraint(
            "organization_contact_id",
            "member_contact_id",
            "role",
            name="uq_organization_membership_role",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    organization_contact_id: Mapped[str] = mapped_column(
        ForeignKey("contacts.id", ondelete="CASCADE"),
        index=True,
    )
    member_contact_id: Mapped[str] = mapped_column(
        ForeignKey("contacts.id", ondelete="CASCADE"),
        index=True,
    )
    role: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )

    organization_contact: Mapped[Contact] = relationship(
        foreign_keys=[organization_contact_id],
        back_populates="organization_memberships",
    )
    member_contact: Mapped[Contact] = relationship(
        foreign_keys=[member_contact_id],
        back_populates="member_memberships",
    )
