from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ContactType = Literal["person", "organization"]
ContactStatus = Literal["active", "archived"]


class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: datetime


class ReadinessResponse(BaseModel):
    status: str
    service: str
    checks: dict[str, str]


class ContactBase(BaseModel):
    contact_type: ContactType = "person"
    display_name: str = Field(min_length=1, max_length=160)
    organization_name: str | None = Field(default=None, max_length=160)
    given_name: str | None = Field(default=None, max_length=100)
    family_name: str | None = Field(default=None, max_length=100)
    status: ContactStatus = "active"


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    contact_type: ContactType | None = None
    display_name: str | None = Field(default=None, min_length=1, max_length=160)
    organization_name: str | None = Field(default=None, max_length=160)
    given_name: str | None = Field(default=None, max_length=100)
    family_name: str | None = Field(default=None, max_length=100)
    status: ContactStatus | None = None


class AddressBase(BaseModel):
    label: str = Field(default="main", min_length=1, max_length=80)
    line1: str = Field(min_length=1, max_length=160)
    line2: str | None = Field(default=None, max_length=160)
    city: str = Field(min_length=1, max_length=120)
    region: str | None = Field(default=None, max_length=120)
    postal_code: str | None = Field(default=None, max_length=40)
    country_code: str = Field(min_length=2, max_length=2)
    is_primary: bool = False


class AddressCreate(AddressBase):
    pass


class AddressUpdate(BaseModel):
    label: str | None = Field(default=None, min_length=1, max_length=80)
    line1: str | None = Field(default=None, min_length=1, max_length=160)
    line2: str | None = Field(default=None, max_length=160)
    city: str | None = Field(default=None, min_length=1, max_length=120)
    region: str | None = Field(default=None, max_length=120)
    postal_code: str | None = Field(default=None, max_length=40)
    country_code: str | None = Field(default=None, min_length=2, max_length=2)
    is_primary: bool | None = None


class CommunicationChannelBase(BaseModel):
    channel_type: str = Field(min_length=1, max_length=40)
    value: str = Field(min_length=1, max_length=200)
    label: str | None = Field(default=None, max_length=80)
    is_primary: bool = False


class CommunicationChannelCreate(CommunicationChannelBase):
    pass


class CommunicationChannelUpdate(BaseModel):
    channel_type: str | None = Field(default=None, min_length=1, max_length=40)
    value: str | None = Field(default=None, min_length=1, max_length=200)
    label: str | None = Field(default=None, max_length=80)
    is_primary: bool | None = None


class TagBase(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    color: str | None = Field(default=None, max_length=20)


class TagCreate(TagBase):
    pass


class TagUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    color: str | None = Field(default=None, max_length=20)


class ActivityBase(BaseModel):
    activity_type: str = Field(default="note", min_length=1, max_length=40)
    body: str = Field(min_length=1)


class ActivityCreate(ActivityBase):
    pass


class ActivityUpdate(BaseModel):
    activity_type: str | None = Field(default=None, min_length=1, max_length=40)
    body: str | None = Field(default=None, min_length=1)


class OrganizationMembershipCreate(BaseModel):
    organization_contact_id: str
    member_contact_id: str
    role: str = Field(min_length=1, max_length=100)


class OrganizationMembershipUpdate(BaseModel):
    role: str | None = Field(default=None, min_length=1, max_length=100)


class TimestampedRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime


class AddressRead(AddressBase, TimestampedRead):
    contact_id: str


class CommunicationChannelRead(CommunicationChannelBase, TimestampedRead):
    contact_id: str


class TagRead(TagBase, TimestampedRead):
    pass


class ActivityRead(ActivityBase, TimestampedRead):
    contact_id: str
    created_by: str


class OrganizationMembershipRead(TimestampedRead):
    organization_contact_id: str
    member_contact_id: str
    role: str


class ContactRead(ContactBase, TimestampedRead):
    addresses: list[AddressRead] = Field(default_factory=list)
    communication_channels: list[CommunicationChannelRead] = Field(default_factory=list)
    tags: list[TagRead] = Field(default_factory=list)


class ContactList(BaseModel):
    items: list[ContactRead]
    total: int
    limit: int
    offset: int


class ContactTypeRead(BaseModel):
    value: ContactType
    label: str
