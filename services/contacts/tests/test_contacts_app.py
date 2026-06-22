from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth import require_scope
from app.database import Base
from app.main import (
    assign_tag,
    create_activity,
    create_address,
    create_communication_channel,
    create_contact,
    create_membership,
    create_tag,
    delete_activity,
    delete_address,
    delete_communication_channel,
    delete_contact,
    delete_membership,
    delete_tag,
    get_contact,
    health,
    list_activity,
    list_addresses,
    list_communication_channels,
    list_contacts,
    list_memberships,
    ready,
    remove_tag,
    update_activity,
    update_address,
    update_communication_channel,
    update_contact,
    update_membership,
)
from app.schemas import (
    ActivityCreate,
    ActivityUpdate,
    AddressCreate,
    AddressUpdate,
    CommunicationChannelCreate,
    CommunicationChannelUpdate,
    ContactCreate,
    ContactUpdate,
    OrganizationMembershipCreate,
    OrganizationMembershipUpdate,
    TagCreate,
)

READ_HEADERS = {"X-OpenVend-Scopes": "contacts:read"}


@pytest.fixture()
def session() -> Generator[Session]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    with session_factory() as db_session:
        yield db_session
    Base.metadata.drop_all(engine)


def new_contact(session: Session, display_name: str = "Ada Lovelace"):
    return create_contact(
        ContactCreate(
            contact_type="person",
            display_name=display_name,
            given_name=display_name.split()[0],
            family_name=display_name.split()[-1],
        ),
        None,
        session,
        "tester",
    )


def test_health_and_ready_are_public(session: Session) -> None:
    health_response = health()
    ready_response = ready(session)

    assert health_response.service == "contacts"
    assert ready_response.status == "ready"


def test_contacts_require_read_scope() -> None:
    dependency = require_scope("contacts:read")

    with pytest.raises(HTTPException) as exc:
        dependency(None)

    assert exc.value.status_code == 401


def test_contacts_accept_read_scope() -> None:
    dependency = require_scope("contacts:read")

    assert dependency(READ_HEADERS["X-OpenVend-Scopes"]) is None


def test_create_list_get_update_and_delete_contact(session: Session) -> None:
    contact = new_contact(session)

    contact_list = list_contacts(None, session, limit=50, offset=0)
    assert contact_list.total == 1

    contact_detail = get_contact(contact.id, None, session)
    assert contact_detail.display_name == "Ada Lovelace"

    updated = update_contact(
        contact.id,
        ContactUpdate(display_name="Ada Byron"),
        None,
        session,
        "tester",
    )
    assert updated.display_name == "Ada Byron"

    delete_response = delete_contact(contact.id, None, session, "tester")
    assert delete_response.status_code == 204
    with pytest.raises(HTTPException) as exc:
        get_contact(contact.id, None, session)
    assert exc.value.status_code == 404


def test_address_crud(session: Session) -> None:
    contact = new_contact(session)

    address = create_address(
        contact.id,
        AddressCreate(
            label="billing",
            line1="1 Analytical Engine Way",
            city="London",
            country_code="GB",
        ),
        None,
        session,
        "tester",
    )
    assert address.city == "London"

    assert len(list_addresses(contact.id, None, session)) == 1

    updated = update_address(
        address.id,
        AddressUpdate(city="Oxford"),
        None,
        session,
        "tester",
    )
    assert updated.city == "Oxford"

    assert delete_address(address.id, None, session, "tester").status_code == 204


def test_communication_channel_crud(session: Session) -> None:
    contact = new_contact(session)

    channel = create_communication_channel(
        contact.id,
        CommunicationChannelCreate(
            channel_type="email",
            value="ada@example.test",
            is_primary=True,
        ),
        None,
        session,
        "tester",
    )
    assert channel.value == "ada@example.test"

    channels = list_communication_channels(contact.id, None, session)
    assert channels[0].value == "ada@example.test"

    updated = update_communication_channel(
        channel.id,
        CommunicationChannelUpdate(value="ada.lovelace@example.test"),
        None,
        session,
        "tester",
    )
    assert updated.value == "ada.lovelace@example.test"

    delete_response = delete_communication_channel(channel.id, None, session, "tester")
    assert delete_response.status_code == 204


def test_tag_crud_and_assignment(session: Session) -> None:
    contact = new_contact(session)

    tag = create_tag(
        TagCreate(name="vip", color="#405cf5"),
        None,
        session,
        "tester",
    )
    assert tag.name == "vip"

    assigned = assign_tag(contact.id, tag.id, None, session, "tester")
    assert assigned.tags[0].name == "vip"

    removed = remove_tag(contact.id, tag.id, None, session, "tester")
    assert removed.tags == []

    with pytest.raises(HTTPException) as exc:
        create_tag(TagCreate(name="vip"), None, session, "tester")
    assert exc.value.status_code == 409

    assert delete_tag(tag.id, None, session, "tester").status_code == 204


def test_activity_crud(session: Session) -> None:
    contact = new_contact(session)

    activity = create_activity(
        contact.id,
        ActivityCreate(activity_type="note", body="Met at conference."),
        None,
        session,
        "tester",
    )
    assert activity.created_by == "tester"

    activities = list_activity(contact.id, None, session)
    assert activities[0].body == "Met at conference."

    updated = update_activity(
        activity.id,
        ActivityUpdate(body="Met at trade show."),
        None,
        session,
        "tester",
    )
    assert updated.body == "Met at trade show."

    assert delete_activity(activity.id, None, session, "tester").status_code == 204


def test_organization_membership_crud(session: Session) -> None:
    organization = new_contact(session, "Analytical Engines Ltd")
    member = new_contact(session, "Ada Lovelace")

    membership = create_membership(
        OrganizationMembershipCreate(
            organization_contact_id=organization.id,
            member_contact_id=member.id,
            role="Founder",
        ),
        None,
        session,
        "tester",
    )
    assert membership.role == "Founder"

    memberships = list_memberships(organization.id, None, session)
    assert memberships[0].member_contact_id == member.id

    updated = update_membership(
        membership.id,
        OrganizationMembershipUpdate(role="Advisor"),
        None,
        session,
        "tester",
    )
    assert updated.role == "Advisor"

    delete_response = delete_membership(membership.id, None, session, "tester")
    assert delete_response.status_code == 204
