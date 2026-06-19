import { readFile } from "node:fs/promises";

const allowed = new Set([
  "MIT",
  "Apache-2.0",
  "BSD-2-Clause",
  "BSD-3-Clause",
  "ISC",
  "Python-2.0",
  "PostgreSQL",
]);

const deniedFragments = ["AGPL", "SSPL", "BUSL", "Commons Clause", "PolyForm", "RSAL"];

async function readPackage(path) {
  return JSON.parse(await readFile(path, "utf8"));
}

const packageFiles = ["apps/web/package.json", "packages/api-client/package.json"];
const violations = [];

for (const file of packageFiles) {
  const pkg = await readPackage(file);
  const declaredLicense = pkg.license;
  if (declaredLicense && !allowed.has(declaredLicense)) {
    violations.push(`${file} declares non-default license ${declaredLicense}`);
  }

  const dependencyNames = [
    ...Object.keys(pkg.dependencies ?? {}),
    ...Object.keys(pkg.devDependencies ?? {}),
  ];
  for (const name of dependencyNames) {
    if (deniedFragments.some((fragment) => name.toLowerCase().includes(fragment.toLowerCase()))) {
      violations.push(`${file} references dependency name matching denied fragment: ${name}`);
    }
  }
}

if (violations.length > 0) {
  console.error("Dependency policy violations:");
  for (const violation of violations) {
    console.error(`- ${violation}`);
  }
  process.exit(1);
}

console.log("Dependency policy check passed.");
