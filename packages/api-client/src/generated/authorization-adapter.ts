// Generated from openapi/authorization-adapter.json.
// Phase 0 keeps this lightweight until the full client generator is introduced.

export const authorizationAdapterOperations = [
  {
    "method": "GET",
    "path": "/health",
    "operationId": "health_health_get"
  },
  {
    "method": "GET",
    "path": "/me",
    "operationId": "me_me_get"
  },
  {
    "method": "GET",
    "path": "/permissions",
    "operationId": "permissions_permissions_get"
  },
  {
    "method": "GET",
    "path": "/ready",
    "operationId": "ready_ready_get"
  },
  {
    "method": "POST",
    "path": "/tokens",
    "operationId": "create_token_tokens_post"
  }
] as const;
