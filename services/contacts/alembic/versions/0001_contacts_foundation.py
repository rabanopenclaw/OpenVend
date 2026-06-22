from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "0001_contacts_foundation"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "contacts",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("contact_type", sa.String(length=32), nullable=False),
        sa.Column("display_name", sa.String(length=160), nullable=False),
        sa.Column("organization_name", sa.String(length=160), nullable=True),
        sa.Column("given_name", sa.String(length=100), nullable=True),
        sa.Column("family_name", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_contacts_contact_type", "contacts", ["contact_type"])
    op.create_index("ix_contacts_display_name", "contacts", ["display_name"])
    op.create_index("ix_contacts_status", "contacts", ["status"])

    op.create_table(
        "tags",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("color", sa.String(length=20), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="uq_tags_name"),
    )

    op.create_table(
        "addresses",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("contact_id", sa.String(length=36), nullable=False),
        sa.Column("label", sa.String(length=80), nullable=False),
        sa.Column("line1", sa.String(length=160), nullable=False),
        sa.Column("line2", sa.String(length=160), nullable=True),
        sa.Column("city", sa.String(length=120), nullable=False),
        sa.Column("region", sa.String(length=120), nullable=True),
        sa.Column("postal_code", sa.String(length=40), nullable=True),
        sa.Column("country_code", sa.String(length=2), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["contact_id"], ["contacts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_addresses_contact_id", "addresses", ["contact_id"])

    op.create_table(
        "communication_channels",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("contact_id", sa.String(length=36), nullable=False),
        sa.Column("channel_type", sa.String(length=40), nullable=False),
        sa.Column("value", sa.String(length=200), nullable=False),
        sa.Column("label", sa.String(length=80), nullable=True),
        sa.Column("is_primary", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["contact_id"], ["contacts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_communication_channels_contact_id",
        "communication_channels",
        ["contact_id"],
    )

    op.create_table(
        "activities",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("contact_id", sa.String(length=36), nullable=False),
        sa.Column("activity_type", sa.String(length=40), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_by", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["contact_id"], ["contacts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_activities_contact_id", "activities", ["contact_id"])

    op.create_table(
        "contact_tags",
        sa.Column("contact_id", sa.String(length=36), nullable=False),
        sa.Column("tag_id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(["contact_id"], ["contacts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("contact_id", "tag_id"),
    )

    op.create_table(
        "organization_memberships",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("organization_contact_id", sa.String(length=36), nullable=False),
        sa.Column("member_contact_id", sa.String(length=36), nullable=False),
        sa.Column("role", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["member_contact_id"], ["contacts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["organization_contact_id"], ["contacts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "organization_contact_id",
            "member_contact_id",
            "role",
            name="uq_organization_membership_role",
        ),
    )
    op.create_index(
        "ix_organization_memberships_member_contact_id",
        "organization_memberships",
        ["member_contact_id"],
    )
    op.create_index(
        "ix_organization_memberships_organization_contact_id",
        "organization_memberships",
        ["organization_contact_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_organization_memberships_organization_contact_id",
        table_name="organization_memberships",
    )
    op.drop_index(
        "ix_organization_memberships_member_contact_id",
        table_name="organization_memberships",
    )
    op.drop_table("organization_memberships")
    op.drop_table("contact_tags")
    op.drop_index("ix_activities_contact_id", table_name="activities")
    op.drop_table("activities")
    op.drop_index(
        "ix_communication_channels_contact_id",
        table_name="communication_channels",
    )
    op.drop_table("communication_channels")
    op.drop_index("ix_addresses_contact_id", table_name="addresses")
    op.drop_table("addresses")
    op.drop_table("tags")
    op.drop_index("ix_contacts_status", table_name="contacts")
    op.drop_index("ix_contacts_display_name", table_name="contacts")
    op.drop_index("ix_contacts_contact_type", table_name="contacts")
    op.drop_table("contacts")
