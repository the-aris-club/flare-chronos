# Glossary Map

This repo uses a **multi-context** layout. Each context owns its own `GLOSSARY.md`; system-wide decisions live in `docs/adr/`, context-specific ones in `<context>/docs/adr/`.

| Context | Glossary | Notes |
| --- | --- | --- |
| root (system-wide / core domain) | [GLOSSARY.md](./GLOSSARY.md) | Cross-sensor harmonization domain: sensor physics, H3 grid, calendar, phenology. |
| harmonization-core | [packages/harmonization-core/GLOSSARY.md](./packages/harmonization-core/GLOSSARY.md) | Created lazily when terms resolve. |
| firms-ingestion | [packages/firms-ingestion/GLOSSARY.md](./packages/firms-ingestion/GLOSSARY.md) | Created lazily when terms resolve. |
| benchmark-cli | [apps/benchmark-cli/GLOSSARY.md](./apps/benchmark-cli/GLOSSARY.md) | Created lazily when terms resolve. |
| harmonization (compat facade) | [src/harmonization/GLOSSARY.md](./src/harmonization/GLOSSARY.md) | Created lazily when terms resolve. |

If a listed `GLOSSARY.md` does not exist yet, proceed silently; `/domain-modeling` creates it lazily.