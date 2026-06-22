from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from sqlalchemy import func, or_, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from .auth import actor_id, require_scope
from .database import get_session
from .models import (
    Activity,
    Address,
    CommunicationChannel,
    Contact,
    OrganizationMembership,
    Tag,
)
from .schemas import (
    ActivityCreate,
    ActivityRead,
    ActivityUpdate,
    AddressCreate,
    AddressRead,
    AddressUpdate,
    CommunicationChannelCreate,
    CommunicationChannelRead,
    CommunicationChannelUpdate,
    ContactCreate,
    ContactList,
    ContactRead,
    ContactTypeRead,
    ContactUpdate,
    HealthResponse,
    OrganizationMembershipCreate,
    OrganizationMembershipRead,
    OrganizationMembershipUpdate,
    ReadinessResponse,
    TagCreate,
    TagRead,
    TagUpdate,
)

SERVICE_NAME = "contacts"
CONTACT_TYPES = (
    ContactTypeRead(value="person", label="Person"),
    ContactTypeRead(value="organization", label="Organization"),
)

logger = logging.getLogger("openvend.contacts")

ReadScope = Depends(require_scope("contacts:read"))
WriteScope = Depends(require_scope("contacts:write"))


def audit_event(
    action: str, actor: str, resource_type: str, resource_id: str, summary: str
) -> None:
    payload = {
        "actor": actor,
        "action": action,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "summary": summary,
    }
    logger.info("audit_event %s", json.dumps(payload, sort_keys=True))


def apply_updates(instance: object, payload: object) -> None:
    for field_name, value in payload.model_dump(exclude_unset=True).items():
        setattr(instance, field_name, value)


def contact_query():
    return select(Contact).options(
        selectinload(Contact.addresses),
        selectinload(Contact.communication_channels),
        selectinload(Contact.tags),
    )


def get_contact_or_404(session: Session, contact_id: str) -> Contact:
    contact = session.scalar(contact_query().where(Contact.id == contact_id))
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")
    return contact


def get_address_or_404(session: Session, address_id: str) -> Address:
    address = session.get(Address, address_id)
    if address is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found.")
    return address


def get_channel_or_404(session: Session, channel_id: str) -> CommunicationChannel:
    channel = session.get(CommunicationChannel, channel_id)
    if channel is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Communication channel not found.",
        )
    return channel


def get_tag_or_404(session: Session, tag_id: str) -> Tag:
    tag = session.get(Tag, tag_id)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found.")
    return tag


def get_activity_or_404(session: Session, activity_id: str) -> Activity:
    activity = session.get(Activity, activity_id)
    if activity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found.")
    return activity


def get_membership_or_404(session: Session, membership_id: str) -> OrganizationMembership:
    membership = session.get(OrganizationMembership, membership_id)
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization membership not found.",
        )
    return membership


app = FastAPI(
    title="OpenVend Contacts Service",
    version="0.1.0",
    summary="Contacts, addresses, communication channels, tags, activity, and memberships.",
)


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    return HealthResponse(status="ok", service=SERVICE_NAME, timestamp=datetime.now(UTC))


@app.get("/ready", response_model=ReadinessResponse, tags=["system"])
def ready(session: Annotated[Session, Depends(get_session)]) -> ReadinessResponse:
    checks = {"database": "ok"}
    try:
        session.execute(text("SELECT 1"))
    except Exception as exc:
        checks["database"] = "error"
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=checks) from exc
    return ReadinessResponse(status="ready", service=SERVICE_NAME, checks=checks)


@app.get("/contact-types", response_model=list[ContactTypeRead], tags=["contacts"])
def list_contact_types(_: Annotated[None, ReadScope]) -> list[ContactTypeRead]:
    return list(CONTACT_TYPES)


@app.get("/contacts", response_model=ContactList, tags=["contacts"])
def list_contacts(
    _: Annotated[None, ReadScope],
    session: Annotated[Session, Depends(get_session)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    contact_type: str | None = None,
    status_filter: Annotated[str | None, Query(alias="status")] = None,
) -> ContactList:
    filters = []
    if contact_type:
        filters.append(Contact.contact_type == contact_type)
    if status_filter:
        filters.append(Contact.status == status_filter)

    total = session.scalar(select(func.count()).select_from(Contact).where(*filters)) or 0
    contacts = list(
        session.scalars(
            contact_query()
            .where(*filters)
            .order_by(Contact.created_at.desc())
            .limit(limit)
            .offset(offset),
        )
    )
    return ContactList(items=contacts, total=total, limit=limit, offset=offset)


@app.post(
    "/contacts", response_model=ContactRead, status_code=status.HTTP_201_CREATED, tags=["contacts"]
)
def create_contact(
    payload: ContactCreate,
    _: Annotated[None, WriteScope],
    session: Annotated[Session, Depends(get_session)],
    actor: Annotated[str, Depends(actor_id)],
) -> Contact:
    contact = Contact(**payload.model_dump())
    session.add(contact)
    session.commit()
    audit_event("contact.create", actor, "contact", contact.id, contact.display_name)
    return get_contact_or_404(session, contact.id)


@app.get("/contacts/{contact_id}", response_model=ContactRead, tags=["contacts"])
def get_contact(
    contact_id: str,
    _: Annotated[None, ReadScope],
    session: Annotated[Session, Depends(get_session)],
) -> Contact:
    return get_contact_or_404(session, contact_id)


@app.patch("/contacts/{contact_id}", response_model=ContactRead, tags=["contacts"])
def update_contact(
    contact_id: str,
    payload: ContactUpdate,
    _: Annotated[None, WriteScope],
    session: Annotated[Session, Depends(get_session)],
    actor: Annotated[str, Depends(actor_id)],
) -> Contact:
    contact = get_contact_or_404(session, contact_id)
    apply_updates(contact, payload)
    session.commit()
    audit_event("contact.update", actor, "contact", contact.id, contact.display_name)
    return get_contact_or_404(session, contact.id)


@app.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["contacts"])
def delete_contact(
    contact_id: str,
    _: Annotated[None, WriteScope],
    session: Annotated[Session, Depends(get_session)],
    actor: Annotated[str, Depends(actor_id)],
) -> Response:
    contact = get_contact_or_404(session, contact_id)
    display_name = contact.display_name
    session.delete(contact)
    session.commit()
    audit_event("contact.delete", actor, "contact", contact_id, display_name)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/contacts/{contact_id}/addresses", response_model=list[AddressRead], tags=["addresses"])
def list_addresses(
    contact_id: str,
    _: Annotated[None, ReadScope],
    session: Annotated[Session, Depends(get_session)],
) -> list[Address]:
    get_contact_or_404(session, contact_id)
    return list(session.scalars(select(Address).where(Address.contact_id == contact_id)))


@app.post(
    "/contacts/{contact_id}/addresses",
    response_model=AddressRead,
    status_code=status.HTTP_201_CREATED,
    tags=["addresses"],
)
def create_address(
    contact_id: str,
    payload: AddressCreate,
    _: Annotated[None, WriteScope],
    session: Annotated[Session, Depends(get_session)],
    actor: Annotated[str, Depends(actor_id)],
) -> Address:
    get_contact_or_404(session, contact_id)
    address = Address(contact_id=contact_id, **payload.model_dump())
    session.add(address)
    session.commit()
    session.refresh(address)
    audit_event("address.create", actor, "address", address.id, contact_id)
    return address


@app.patch("/addresses/{address_id}", response_model=AddressRead, tags=["addresses"])
def update_address(
    address_id: str,
    payload: AddressUpdate,
    _: Annotated[None, WriteScope],
    session: Annotated[Session, Depends(get_session)],
    actor: Annotated[str, Depends(actor_id)],
) -> Address:
    address = get_address_or_404(session, address_id)
    apply_updates(address, payload)
    session.commit()
    session.refresh(address)
    audit_event("address.update", actor, "address", address.id, address.contact_id)
    return address


@app.delete("/addresses/{address_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["addresses"])
def delete_address(
    address_id: str,
    _: Annotated[None, WriteScope],
    session: Annotated[Session, Depends(get_session)],
    actor: Annotated[str, Depends(actor_id)],
) -> Response:
    address = get_address_or_404(session, address_id)
    contact_id = address.contact_id
    session.delete(address)
    session.commit()
    audit_event("address.delete", actor, "address", address_id, contact_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get(
    "/contacts/{contact_id}/communication-channels",
    response_model=list[CommunicationChannelRead],
    tags=["communication-channels"],
)
def list_communication_channels(
    contact_id: str,
    _: Annotated[None, ReadScope],
    session: Annotated[Session, Depends(get_session)],
) -> list[CommunicationChannel]:
    get_contact_or_404(session, contact_id)
    return list(
        session.scalars(
            select(CommunicationChannel).where(CommunicationChannel.contact_id == contact_id)
        )
    )


@app.post(
    "/contacts/{contact_id}/communication-channels",
    response_model=CommunicationChannelRead,
    status_code=status.HTTP_201_CREATED,
    tags=["communication-channels"],
)
def create_communication_channel(
    contact_id: str,
    payload: CommunicationChannelCreate,
    _: Annotated[None, WriteScope],
    session: Annotated[Session, Depends(get_session)],
    actor: Annotated[str, Depends(actor_id)],
) -> CommunicationChannel:
    get_contact_or_404(session, contact_id)
    channel = CommunicationChannel(contact_id=contact_id, **payload.model_dump())
    session.add(channel)
    session.commit()
    session.refresh(channel)
    audit_event(
        "communication_channel.create", actor, "communication_channel", channel.id, contact_id
    )
    return channel


@app.patch(
    "/communication-channels/{channel_id}",
    response_model=CommunicationChannelRead,
    tags=["communication-channels"],
)
def update_communication_channel(
    channel_id: str,
    payload: CommunicationChannelUpdate,
    _: Annotated[None, WriteScope],
    session: Annotated[Session, Depends(get_session)],
    actor: Annotated[str, Depends(actor_id)],
) -> CommunicationChannel:
    channel = get_channel_or_404(session, channel_id)
    apply_updates(channel, payload)
    session.commit()
    session.refresh(channel)
    audit_event(
        "communication_channel.update",
        actor,
        "communication_channel",
        channel.id,
        channel.contact_id,
    )
    return channel


@app.delete(
    "/communication-channels/{channel_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["communication-channels"],
)
def delete_communication_channel(
    channel_id: str,
    _: Annotated[None, WriteScope],
    session: Annotated[Session, Depends(get_session)],
    actor: Annotated[str, Depends(actor_id)],
) -> Response:
    channel = get_channel_or_404(session, channel_id)
    contact_id = channel.contact_id
    session.delete(channel)
    session.commit()
    audit_event(
        "communication_channel.delete", actor, "communication_channel", channel_id, contact_id
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/tags", response_model=list[TagRead], tags=["tags"])
def list_tags(
    _: Annotated[None, ReadScope], session: Annotated[Session, Depends(get_session)]
) -> list[Tag]:
    return list(session.scalars(select(Tag).order_by(Tag.name.asc())))


@app.post("/tags", response_model=TagRead, status_code=status.HTTP_201_CREATED, tags=["tags"])
def create_tag(
    payload: TagCreate,
    _: Annotated[None, WriteScope],
    session: Annotated[Session, Depends(get_session)],
    actor: Annotated[str, Depends(actor_id)],
) -> Tag:
    tag = Tag(**payload.model_dump())
    session.add(tag)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Tag already exists."
        ) from exc
    session.refresh(tag)
    audit_event("tag.create", actor, "tag", tag.id, tag.name)
    return tag


@app.patch("/tags/{tag_id}", response_model=TagRead, tags=["tags"])
def update_tag(
    tag_id: str,
    payload: TagUpdate,
    _: Annotated[None, WriteScope],
    session: Annotated[Session, Depends(get_session)],
    actor: Annotated[str, Depends(actor_id)],
) -> Tag:
    tag = get_tag_or_404(session, tag_id)
    apply_updates(tag, payload)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Tag already exists."
        ) from exc
    session.refresh(tag)
    audit_event("tag.update", actor, "tag", tag.id, tag.name)
    return tag


@app.delete("/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tags"])
def delete_tag(
    tag_id: str,
    _: Annotated[None, WriteScope],
    session: Annotated[Session, Depends(get_session)],
    actor: Annotated[str, Depends(actor_id)],
) -> Response:
    tag = get_tag_or_404(session, tag_id)
    name = tag.name
    session.delete(tag)
    session.commit()
    audit_event("tag.delete", actor, "tag", tag_id, name)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post("/contacts/{contact_id}/tags/{tag_id}", response_model=ContactRead, tags=["tags"])
def assign_tag(
    contact_id: str,
    tag_id: str,
    _: Annotated[None, WriteScope],
    session: Annotated[Session, Depends(get_session)],
    actor: Annotated[str, Depends(actor_id)],
) -> Contact:
    contact = get_contact_or_404(session, contact_id)
    tag = get_tag_or_404(session, tag_id)
    if tag not in contact.tags:
        contact.tags.append(tag)
        session.commit()
        audit_event("contact_tag.assign", actor, "contact", contact.id, tag.name)
    return get_contact_or_404(session, contact_id)


@app.delete("/contacts/{contact_id}/tags/{tag_id}", response_model=ContactRead, tags=["tags"])
def remove_tag(
    contact_id: str,
    tag_id: str,
    _: Annotated[None, WriteScope],
    session: Annotated[Session, Depends(get_session)],
    actor: Annotated[str, Depends(actor_id)],
) -> Contact:
    contact = get_contact_or_404(session, contact_id)
    tag = get_tag_or_404(session, tag_id)
    if tag in contact.tags:
        contact.tags.remove(tag)
        session.commit()
        audit_event("contact_tag.remove", actor, "contact", contact.id, tag.name)
    return get_contact_or_404(session, contact_id)


@app.get("/contacts/{contact_id}/activity", response_model=list[ActivityRead], tags=["activity"])
def list_activity(
    contact_id: str,
    _: Annotated[None, ReadScope],
    session: Annotated[Session, Depends(get_session)],
) -> list[Activity]:
    get_contact_or_404(session, contact_id)
    return list(
        session.scalars(
            select(Activity)
            .where(Activity.contact_id == contact_id)
            .order_by(Activity.created_at.desc()),
        )
    )


@app.post(
    "/contacts/{contact_id}/activity",
    response_model=ActivityRead,
    status_code=status.HTTP_201_CREATED,
    tags=["activity"],
)
def create_activity(
    contact_id: str,
    payload: ActivityCreate,
    _: Annotated[None, WriteScope],
    session: Annotated[Session, Depends(get_session)],
    actor: Annotated[str, Depends(actor_id)],
) -> Activity:
    get_contact_or_404(session, contact_id)
    activity = Activity(contact_id=contact_id, created_by=actor, **payload.model_dump())
    session.add(activity)
    session.commit()
    session.refresh(activity)
    audit_event("activity.create", actor, "activity", activity.id, contact_id)
    return activity


@app.patch("/activity/{activity_id}", response_model=ActivityRead, tags=["activity"])
def update_activity(
    activity_id: str,
    payload: ActivityUpdate,
    _: Annotated[None, WriteScope],
    session: Annotated[Session, Depends(get_session)],
    actor: Annotated[str, Depends(actor_id)],
) -> Activity:
    activity = get_activity_or_404(session, activity_id)
    apply_updates(activity, payload)
    session.commit()
    session.refresh(activity)
    audit_event("activity.update", actor, "activity", activity.id, activity.contact_id)
    return activity


@app.delete("/activity/{activity_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["activity"])
def delete_activity(
    activity_id: str,
    _: Annotated[None, WriteScope],
    session: Annotated[Session, Depends(get_session)],
    actor: Annotated[str, Depends(actor_id)],
) -> Response:
    activity = get_activity_or_404(session, activity_id)
    contact_id = activity.contact_id
    session.delete(activity)
    session.commit()
    audit_event("activity.delete", actor, "activity", activity_id, contact_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get(
    "/contacts/{contact_id}/memberships",
    response_model=list[OrganizationMembershipRead],
    tags=["organization-memberships"],
)
def list_memberships(
    contact_id: str,
    _: Annotated[None, ReadScope],
    session: Annotated[Session, Depends(get_session)],
) -> list[OrganizationMembership]:
    get_contact_or_404(session, contact_id)
    return list(
        session.scalars(
            select(OrganizationMembership).where(
                or_(
                    OrganizationMembership.organization_contact_id == contact_id,
                    OrganizationMembership.member_contact_id == contact_id,
                )
            )
        )
    )


@app.post(
    "/organization-memberships",
    response_model=OrganizationMembershipRead,
    status_code=status.HTTP_201_CREATED,
    tags=["organization-memberships"],
)
def create_membership(
    payload: OrganizationMembershipCreate,
    _: Annotated[None, WriteScope],
    session: Annotated[Session, Depends(get_session)],
    actor: Annotated[str, Depends(actor_id)],
) -> OrganizationMembership:
    get_contact_or_404(session, payload.organization_contact_id)
    get_contact_or_404(session, payload.member_contact_id)
    membership = OrganizationMembership(**payload.model_dump())
    session.add(membership)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Organization membership already exists.",
        ) from exc
    session.refresh(membership)
    audit_event(
        "organization_membership.create",
        actor,
        "organization_membership",
        membership.id,
        membership.role,
    )
    return membership


@app.patch(
    "/organization-memberships/{membership_id}",
    response_model=OrganizationMembershipRead,
    tags=["organization-memberships"],
)
def update_membership(
    membership_id: str,
    payload: OrganizationMembershipUpdate,
    _: Annotated[None, WriteScope],
    session: Annotated[Session, Depends(get_session)],
    actor: Annotated[str, Depends(actor_id)],
) -> OrganizationMembership:
    membership = get_membership_or_404(session, membership_id)
    apply_updates(membership, payload)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Organization membership already exists.",
        ) from exc
    session.refresh(membership)
    audit_event(
        "organization_membership.update",
        actor,
        "organization_membership",
        membership.id,
        membership.role,
    )
    return membership


@app.delete(
    "/organization-memberships/{membership_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["organization-memberships"],
)
def delete_membership(
    membership_id: str,
    _: Annotated[None, WriteScope],
    session: Annotated[Session, Depends(get_session)],
    actor: Annotated[str, Depends(actor_id)],
) -> Response:
    membership = get_membership_or_404(session, membership_id)
    role = membership.role
    session.delete(membership)
    session.commit()
    audit_event(
        "organization_membership.delete", actor, "organization_membership", membership_id, role
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
