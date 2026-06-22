// Generated from openapi/contacts.json.
// Phase 1 keeps this lightweight until the full client generator is introduced.

export const contactsOperations = [
  {
    "method": "DELETE",
    "path": "/activity/{activity_id}",
    "operationId": "delete_activity_activity__activity_id__delete"
  },
  {
    "method": "PATCH",
    "path": "/activity/{activity_id}",
    "operationId": "update_activity_activity__activity_id__patch"
  },
  {
    "method": "DELETE",
    "path": "/addresses/{address_id}",
    "operationId": "delete_address_addresses__address_id__delete"
  },
  {
    "method": "PATCH",
    "path": "/addresses/{address_id}",
    "operationId": "update_address_addresses__address_id__patch"
  },
  {
    "method": "DELETE",
    "path": "/communication-channels/{channel_id}",
    "operationId": "delete_communication_channel_communication_channels__channel_id__delete"
  },
  {
    "method": "PATCH",
    "path": "/communication-channels/{channel_id}",
    "operationId": "update_communication_channel_communication_channels__channel_id__patch"
  },
  {
    "method": "GET",
    "path": "/contact-types",
    "operationId": "list_contact_types_contact_types_get"
  },
  {
    "method": "GET",
    "path": "/contacts",
    "operationId": "list_contacts_contacts_get"
  },
  {
    "method": "POST",
    "path": "/contacts",
    "operationId": "create_contact_contacts_post"
  },
  {
    "method": "DELETE",
    "path": "/contacts/{contact_id}",
    "operationId": "delete_contact_contacts__contact_id__delete"
  },
  {
    "method": "GET",
    "path": "/contacts/{contact_id}",
    "operationId": "get_contact_contacts__contact_id__get"
  },
  {
    "method": "PATCH",
    "path": "/contacts/{contact_id}",
    "operationId": "update_contact_contacts__contact_id__patch"
  },
  {
    "method": "GET",
    "path": "/contacts/{contact_id}/activity",
    "operationId": "list_activity_contacts__contact_id__activity_get"
  },
  {
    "method": "POST",
    "path": "/contacts/{contact_id}/activity",
    "operationId": "create_activity_contacts__contact_id__activity_post"
  },
  {
    "method": "GET",
    "path": "/contacts/{contact_id}/addresses",
    "operationId": "list_addresses_contacts__contact_id__addresses_get"
  },
  {
    "method": "POST",
    "path": "/contacts/{contact_id}/addresses",
    "operationId": "create_address_contacts__contact_id__addresses_post"
  },
  {
    "method": "GET",
    "path": "/contacts/{contact_id}/communication-channels",
    "operationId": "list_communication_channels_contacts__contact_id__communication_channels_get"
  },
  {
    "method": "POST",
    "path": "/contacts/{contact_id}/communication-channels",
    "operationId": "create_communication_channel_contacts__contact_id__communication_channels_post"
  },
  {
    "method": "GET",
    "path": "/contacts/{contact_id}/memberships",
    "operationId": "list_memberships_contacts__contact_id__memberships_get"
  },
  {
    "method": "DELETE",
    "path": "/contacts/{contact_id}/tags/{tag_id}",
    "operationId": "remove_tag_contacts__contact_id__tags__tag_id__delete"
  },
  {
    "method": "POST",
    "path": "/contacts/{contact_id}/tags/{tag_id}",
    "operationId": "assign_tag_contacts__contact_id__tags__tag_id__post"
  },
  {
    "method": "GET",
    "path": "/health",
    "operationId": "health_health_get"
  },
  {
    "method": "POST",
    "path": "/organization-memberships",
    "operationId": "create_membership_organization_memberships_post"
  },
  {
    "method": "DELETE",
    "path": "/organization-memberships/{membership_id}",
    "operationId": "delete_membership_organization_memberships__membership_id__delete"
  },
  {
    "method": "PATCH",
    "path": "/organization-memberships/{membership_id}",
    "operationId": "update_membership_organization_memberships__membership_id__patch"
  },
  {
    "method": "GET",
    "path": "/ready",
    "operationId": "ready_ready_get"
  },
  {
    "method": "GET",
    "path": "/tags",
    "operationId": "list_tags_tags_get"
  },
  {
    "method": "POST",
    "path": "/tags",
    "operationId": "create_tag_tags_post"
  },
  {
    "method": "DELETE",
    "path": "/tags/{tag_id}",
    "operationId": "delete_tag_tags__tag_id__delete"
  },
  {
    "method": "PATCH",
    "path": "/tags/{tag_id}",
    "operationId": "update_tag_tags__tag_id__patch"
  }
] as const;
