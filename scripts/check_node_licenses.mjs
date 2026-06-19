import { init as checkLicenses } from "license-checker-rseidelsohn";

const deniedFragments = [
  "AGPL",
  "SSPL",
  "BUSL",
  "Commons Clause",
  "PolyForm",
  "RSAL",
];

const packages = await new Promise((resolve, reject) => {
  checkLicenses(
    {
      start: process.cwd(),
      excludePrivatePackages: true,
    },
    (error, results) => {
      if (error) {
        reject(error);
        return;
      }
      resolve(results);
    },
  );
});
const violations = [];

for (const [name, metadata] of Object.entries(packages)) {
  const license = String(metadata.licenses ?? "UNKNOWN");
  if (deniedFragments.some((fragment) => license.toLowerCase().includes(fragment.toLowerCase()))) {
    violations.push(`${name}: ${license}`);
  }
}

if (violations.length > 0) {
  console.error("Node dependency license policy violations:");
  for (const violation of violations) {
    console.error(`- ${violation}`);
  }
  process.exit(1);
}

console.log(`Node dependency license check passed for ${Object.keys(packages).length} packages.`);
