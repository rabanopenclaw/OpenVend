import { mkdir, readdir, readFile, writeFile } from "node:fs/promises";
import { basename, dirname } from "node:path";

const openapiDir = new URL("../../../openapi/", import.meta.url);
const generatedDir = new URL("../src/generated/", import.meta.url);

function exportName(serviceName) {
  return `${serviceName.replace(/-([a-z])/g, (_, letter) => letter.toUpperCase())}Operations`;
}

const specFiles = (await readdir(openapiDir)).filter((fileName) => fileName.endsWith(".json")).sort();

await mkdir(generatedDir, { recursive: true });

for (const fileName of specFiles) {
  const serviceName = basename(fileName, ".json");
  const source = new URL(fileName, openapiDir);
  const target = new URL(`${serviceName}.ts`, generatedDir);
  const spec = JSON.parse(await readFile(source, "utf8"));
  const operations = Object.entries(spec.paths ?? {}).flatMap(([path, methods]) =>
    Object.entries(methods).map(([method, operation]) => ({
      method: method.toUpperCase(),
      path,
      operationId: operation.operationId,
    })),
  );

  const content = `// Generated from openapi/${fileName}.
// Phase 1 keeps this lightweight until the full client generator is introduced.

export const ${exportName(serviceName)} = ${JSON.stringify(operations, null, 2)} as const;
`;

  await mkdir(dirname(target.pathname), { recursive: true });
  await writeFile(target, content);

  console.log(`Generated ${operations.length} ${serviceName} operations.`);
}
