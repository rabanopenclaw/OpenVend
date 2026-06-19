import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname } from "node:path";

const source = new URL("../../../openapi/authorization-adapter.json", import.meta.url);
const target = new URL("../src/generated/authorization-adapter.ts", import.meta.url);

const spec = JSON.parse(await readFile(source, "utf8"));
const operations = Object.entries(spec.paths ?? {}).flatMap(([path, methods]) =>
  Object.entries(methods).map(([method, operation]) => ({
    method: method.toUpperCase(),
    path,
    operationId: operation.operationId,
  })),
);

const content = `// Generated from openapi/authorization-adapter.json.
// Phase 0 keeps this lightweight until the full client generator is introduced.

export const authorizationAdapterOperations = ${JSON.stringify(operations, null, 2)} as const;
`;

await mkdir(dirname(target.pathname), { recursive: true });
await writeFile(target, content);

console.log(`Generated ${operations.length} Authorization Adapter operations.`);
