export type HealthResponse = {
  status: string;
  service: string;
  timestamp: string;
};

export { authorizationAdapterOperations } from "./generated/authorization-adapter";
export { contactsOperations } from "./generated/contacts";

export async function getAuthorizationHealth(baseUrl = "/api/v1/authz"): Promise<HealthResponse> {
  const response = await fetch(`${baseUrl}/health`);
  if (!response.ok) {
    throw new Error(`Authorization health check failed: ${response.status}`);
  }
  return response.json() as Promise<HealthResponse>;
}
