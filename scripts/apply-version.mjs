// Runs after `changeset version` inside the Version Packages PR:
// stamps the new version + date into the exported Markdown headers, rebuilds
// are handled by `pnpm run doc:version`, and propagates the version to every
// package.json / pyproject.toml in the monorepo.
import { readFileSync, writeFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";

const version = JSON.parse(readFileSync("package.json", "utf8")).version;
const now = new Date();
const date = [
  String(now.getDate()).padStart(2, "0"),
  String(now.getMonth() + 1).padStart(2, "0"),
  now.getFullYear(),
].join("/");

const mdFiles = [
  "exports/PROPOSAL.md",
  "exports/REPORT.md",
  "exports/MODEL_FLOW.md",
];
for (const mdPath of mdFiles) {
  try {
    let md = readFileSync(mdPath, "utf8");
    const versionLine = `> **Phiên bản:** \`v${version}\` — cập nhật ${date}`;
    if (/^> \*\*Phiên bản:\*\*.*$/m.test(md)) {
      md = md.replace(/^> \*\*Phiên bản:\*\*.*$/m, versionLine);
    } else {
      md = md.replace(/^(> .*\n)/m, `$1${versionLine}\n`);
    }
    writeFileSync(mdPath, md);
    console.log(`apply-version: v${version} stamped into ${mdPath} (${date})`);
  } catch (err) {
    console.error(`apply-version: could not update ${mdPath}:`, err);
  }
}

// Propagate version to all package.json / pyproject.toml files.
function walk(dir, cb) {
  for (const name of readdirSync(dir)) {
    const full = join(dir, name);
    const st = statSync(full);
    if (st.isDirectory()) {
      if (name === "node_modules" || name === ".git" || name === ".venv")
        continue;
      walk(full, cb);
    } else {
      cb(full);
    }
  }
}

walk(".", (file) => {
  if (file.endsWith("package.json")) {
    try {
      const raw = readFileSync(file, "utf8");
      const json = JSON.parse(raw);
      if (typeof json.version === "string" && json.version !== version) {
        const updated = raw.replace(
          /"version"\s*:\s*"[^"]*"/,
          `"version": "${version}"`
        );
        if (updated !== raw) {
          writeFileSync(file, updated);
          console.log(`apply-version: ${file} -> ${version}`);
        }
      }
    } catch {
      // ignore non-JSON or unreadable files
    }
  } else if (file.endsWith("pyproject.toml")) {
    const raw = readFileSync(file, "utf8");
    const updated = raw.replace(
      /^version\s*=\s*"[^"]*"/m,
      `version = "${version}"`
    );
    if (updated !== raw) {
      writeFileSync(file, updated);
      console.log(`apply-version: ${file} -> ${version}`);
    }
  }
});
