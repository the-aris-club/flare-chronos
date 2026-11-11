# flare-chronos

## 2.0.1

### Patch Changes

- 5e1452e: 09/11/2026 — exports/REPORT.md — added: References section with the NASA challenge, LANCE FIRMS APIs and archive, the ERA5 cloud resource, the published literature and the GitHub repository
  09/11/2026 — exports/PROPOSAL.md — added: References section with the NASA challenge, LANCE FIRMS APIs and archive, the ERA5 cloud resource, the published literature and the GitHub repository
- 5d240e9: 09/11/2026 — apps/workbench/src — fixed: shortened motion and respected reduced motion

## 2.0.0

### Major Changes

- 05/11/2026 — exports/MODEL_FLOW.md — removed: merged model flow into REPORT.md, single compact report
  05/11/2026 — exports/REPORT.md — replaced: compact report with the merged model flow and balanced table columns
  05/11/2026 — exports/PROPOSAL.md — updated: compact English submission draft with balanced table columns

## 1.1.2

### Patch Changes

- c2cb9ca: 04/11/2026 — exports/PROPOSAL.md — updated: compact English submission draft with balanced table columns
  04/11/2026 — exports/REPORT.md — updated: compact report with the merged model flow and balanced table columns

## 1.1.1

### Patch Changes

- f76d780: 04/11/2026 — exports/PROPOSAL.md — updated: English conversion, NASA Space Apps 2026 submission metadata, SSOT canonical metrics, and Workbench preview
  04/11/2026 — exports/REPORT.md — updated: English conversion, 8-column table fix, SSOT canonical metrics, and Workbench preview
  04/11/2026 — exports/MODEL_FLOW.md — updated: English conversion, Mermaid subgraph fix, and 22-use-case / 27-tool alignment

## 1.1.0

### Minor Changes

- 3c2925f: 02/11/2026 — docs/01_NASA_SpaceApps_Proposal.md — updated: added Appendix A, per-region tables of 25 Measured Epochs; 2026 is an Interpolated Year
  02/11/2026 — docs/02_Cross_Sensor_Harmonization_Spec.md — updated: calibration on 20,552 Aqua–SNPP pairs; the 95% confidence interval of the RMSE reduction on the holdout sample includes zero
  02/11/2026 — docs/05_Pitch_Deck_and_Video_Script.md — updated: pair count, D_KS and the 69.8% reduction for the new dataset
  02/11/2026 — exports/PROPOSAL.md — updated: aligned with the new calibration figures
  02/11/2026 — exports/REPORT.md — updated: aligned with the new calibration figures
  02/11/2026 — README.md — updated: the FIRMS Mekong query box extends south to 8.5°N to include the Mekong Delta

### Patch Changes

- ffb3efc: 03/11/2026 — apps/workbench — updated: resolve all lint errors/warnings without config ignores
- 3a4a39c: 03/11/2026 — exports/PROPOSAL.md — updated: FIRMS query box and headline numbers
  03/11/2026 — exports/REPORT.md — updated: FIRMS query box and headline numbers
- 6f00425: 01/11/2026 — exports/MODEL_FLOW.md — updated: the Workbench reads the event stream instead of the HTML demo page
  01/11/2026 — exports/PROPOSAL.md — updated: the Workbench is described as an event-stream client; the service ships no HTML page
  01/11/2026 — exports/REPORT.md — updated: removed the demo/index.html entry from the directory tree
- 96af572: 03/11/2026 — apps/workbench/tsconfig.json — updated: include test files in type check and add bun types

## 1.0.0

### Major Changes

- 67025be: 23/10/2026 — exports/MODEL_FLOW.md — updated: finalized the two-generation flow model for the v1.0.0 release
- 67025be: 23/10/2026 — exports/PROPOSAL.md — updated: finalized the harmonization pipeline for the v1.0.0 release
- 67025be: 23/10/2026 — exports/REPORT.md — updated: finalized the architecture and validation figures for the v1.0.0 release

Change log for the documents submitted outside this repo.

Entry format: `[<hash>: ]dd/mm/yyyy — <file> — <action>: <summary>`; the `<hash>: ` prefix names the commit that changed the document (optional).
Actions: `added` | `fixed` | `removed` | `replaced` | `updated`.
