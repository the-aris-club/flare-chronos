<p align="center">
  <img src="docs/figures/flare-chronos-logo.png" alt="Flare-Chronos Official Logo — 26-Year Harmonized Burning Activity Calendar" width="320" />
</p>

<h1 align="center">Flare-Chronos</h1>

<p align="center">
  <strong>Fire Long-term Archive Resolution &amp; Cross-sensor Harmonization for Operational Near-real-time Observation System</strong>
</p>

> A 26-year, cross-sensor (MODIS + VIIRS) harmonized Burning Activity Calendar & Dual-System Cognitive AI Harness built on NASA FIRMS data — turning 25+ years of heterogeneous satellite active-fire observations into a single, physics-calibrated, sensor-invariant record.

<p align="center">
  <a href="https://github.com/the-aris-club/flare-chronos/actions/workflows/ci.yml"><img src="https://github.com/the-aris-club/flare-chronos/actions/workflows/ci.yml/badge.svg" alt="CI" /></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.11%2B-blue" alt="Python" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="License" /></a>
  <a href="exports/PROPOSAL.pdf"><img src="https://img.shields.io/badge/PDF-PROPOSAL-ea580c" alt="Proposal PDF" /></a>
  <a href="exports/REPORT.pdf"><img src="https://img.shields.io/badge/PDF-REPORT-1d4ed8" alt="Report PDF" /></a>
</p>

---

## Table of Contents

- [Overview](#overview)
- [Name & Acronym Meaning](#name--acronym-meaning)
- [Features](#features)
- [Architecture](#architecture)
- [Repository Layout](#repository-layout)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Data](#data)
- [Testing](#testing)
- [Linting, Formatting & Type Checking](#linting-formatting--type-checking)
- [CI / CD](#ci--cd)
- [Domain Glossary & ADRs](#domain-glossary--adrs)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**Flare-Chronos** addresses the *Harmonization of MODIS and VIIRS Hot Spots* challenge (2026 NASA Space Apps Challenge). Satellite active-fire records spanning 2000–2026+ are fragmented across multiple sensors (MODIS on Terra/Aqua, VIIRS on Suomi-NPP/NOAA-20/NOAA-21) with incompatible spatial footprints, radiometric calibration, scan geometry, and orbital coverage. Naively summing detections creates artificial trends (e.g. the +SNPP step in 2012, +NOAA-20/21 steps in 2020/2024).

Flare-Chronos resolves this by:

1. Reconstructing each detector's **instantaneous elliptical footprint** from scan angle (MODIS bow-tie, VIIRS 3-zone aggregation).
2. Allocating footprints fractionally onto the **Uber H3** discrete global grid.
3. Reclassifying day/night via astronomical **Solar Zenith Angle** (SZA < 85°).
4. Filtering noise (South Atlantic Anomaly, static thermal sources) with a unified **P(fire)**.
5. Applying a **two-stage physics-guided FRP calibration** (scan-angle observation operator + stratified quantile mapping Aqua→SNPP).
6. Clustering multi-satellite overpasses into **Fire Episodes** and normalizing by **Effective Observation Effort Ω**.
7. Producing a **Burning Activity Calendar** (Year × 73 Pentads) with Harmonized Fire Density (HFD), Harmonized Radiative Flux (HRF), and Standardized Fire Anomaly Index (SFAI).

---

## Name & Acronym Meaning

- **FLARE** — evokes the image of a flame (ngọn lửa): the fire signal the system detects, harmonizes, and tracks.
- **CHRONOS** — emphasizes the core deliverable, the *Burning Activity Calendar* (Lịch hoạt động cháy), spanning more than 25 years of active-fire history (2000–2026+).
- The system connects and harmonizes data from the **NASA FIRMS** (Fire Information for Resource Management System) archive and near-real-time streams into one sensor-invariant, physics-calibrated record.

See [`docs/00_Project_Name_and_Acronym.md`](docs/00_Project_Name_and_Acronym.md) and [`GLOSSARY.md`](GLOSSARY.md).

---

## Features

- **Multi-sensor ingestion**: MODIS C6.1 (Terra/Aqua), VIIRS 375m C2 (Suomi-NPP, NOAA-20, NOAA-21), NRT/URT streams, open 7-day regional feeds.
- **Physics-based footprint reconstruction**: spherical scan geometry, bow-tie distortion, VIIRS 3-zone aggregation (3:1 / 2:1 / 1:1).
- **H3 fractional allocation**: energy-conserving allocation to Uber H3 Res 7 / Res 8 cells.
- **Astronomical day/night unification**: SZA < 85° reclassification.
- **Noise rejection**: SAA cosmic-ray spike filter, static thermal source filter, unified P(fire).
- **Two-stage FRP calibration**: scan-angle observation operator + stratified quantile mapping (Aqua→SNPP).
- **Spatio-temporal deduplication**: multi-satellite overpass clustering into Fire Episodes (τ = 95 min).
- **Effort normalization**: Ω(year, latitude) prevents constellation-expansion artificial trends.
- **Burning Activity Calendar**: 26 Years × 73 Pentads matrix of HFD / HRF / SFAI with robust seasonal Z-scores.
- **Dual-System Cognitive AI Harness (`apps/ai-service`)**: LangGraph orchestration pairing a **System 1 classifier** (reflexive triage and entity extraction) with a **System 2 native chat endpoint** (deliberative reasoning) across **20 Use Cases** and **23 deterministic `@tool` functions**. The model chooses its own tool calls; the harness only decides which tools each tier may reach. Every briefing is a **Grounded Narrative**: the model authors the interpretation while the harness injects every quantity from the `VerifiedFactsLedger`, checked by a `NumericGroundingVerifier`. Briefings that authorize a field action pause for a **human sign-off** before they are released. Each layer is bound through an **Endpoint Profile** (protocol, endpoint, model, API key, request options) resolved from explicit configuration only — never from the host's agent tooling configuration ([ADR-0006](docs/adr/0006-explicit-endpoint-profiles-and-grounded-narrative-assembly.md), [ADR-0008](docs/adr/0008-model-driven-tool-selection-sign-off-and-event-stream.md)).
- **Deep-module monorepo**: pure core (zero I/O) behind a clean seam; ingestion adapter; benchmark CLI; dual-system AI service; PDF exports (`exports/PROPOSAL.pdf` & `exports/REPORT.pdf`).

---

## Architecture

See [`docs/03_System_Architecture_and_Data_Pipeline.md`](docs/03_System_Architecture_and_Data_Pipeline.md) and [`exports/REPORT.md`](exports/REPORT.md) for the full end-to-end pipeline, DuckDB/H3 schema, Dual-System LangGraph Harness, and REST API specification.

High-level flow:

```
NASA FIRMS (MODIS / VIIRS / NRT) ──► firms-ingestion (rate-limited, cached)
                                            │
                                            ▼
                              harmonization-core (deep module)
        SZA unification → P(fire) filtering → footprint reconstruction →
        H3 allocation → two-stage FRP calibration → episode clustering →
        effort normalization → Burning Activity Calendar
                                            │
                                            ▼
                     ai-service (LangGraph System 1 ↔ System 2)
        24 deterministic @tools → VerifiedFactsLedger → NumericGroundingVerifier
                                            │
                                            ▼
                              DuckDB / Parquet cube + REST API + Deck.gl UI
```

---

## Repository Layout

```
flare-chronos/
├── GLOSSARY.md / GLOSSARY-MAP.md      # Domain ubiquitous language (multi-context)
├── AGENTS.md                          # Agent skills config
├── pyproject.toml                     # uv workspace root
├── packages/
│   ├── harmonization-core/            # [Deep Module] pure physics/math (zero I/O)
│   └── firms-ingestion/               # [Adapter Seam] NASA LANCE FIRMS client + cache
├── apps/
│   ├── benchmark-cli/                 # [Application] data fetch, experiments, figures
│   └── ai-service/                    # [Cognitive Layer] LangGraph System 1 + System 2 (20 UCs, 24 @tools)
├── exports/
│   ├── PROPOSAL.md / PROPOSAL.pdf     # Official Technical Proposal (Vietnamese A4 PDF)
│   ├── REPORT.md / REPORT.pdf         # Codebase Architecture & Empirical Report (A4 PDF)
│   └── export_pdf.py                  # Vector SVG + WeasyPrint A4 PDF compiler
├── src/harmonization/                 # [Compat Seam] facade for auto-grading
├── tests/                             # 26 unit, invariant, harness & live TDD seam tests
├── docs/                              # Proposal, specs, ADRs (0001-0007), figures & logo
│   └── media/SOURCES.md               # Editorial deliverable index & naming convention
└── .github/workflows/ci.yml           # CI
```

---

## Getting Started

### Prerequisites

- Python >= 3.11
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- (Optional) `ruff`, `pyright`, `pytest` — installed via dev deps

### Install

```bash
git clone https://github.com/the-aris-club/flare-chronos.git
cd flare-chronos
uv sync --group dev
```

### Environment

Copy `.env.example` to `.env` and set your NASA FIRMS MAP key:

```bash
cp .env.example .env
# edit .env: FIRMS_MAP_KEY=your_32_char_key
```

---

## Usage

### Run the test suite

```bash
uv run python -m pytest
```

### Run experiments / generate figures

```bash
uv run python -m benchmark_cli.run_experiments
```

### Fetch real FIRMS data

```bash
uv run python -m benchmark_cli.fetch_real_firms
```

### Lint / format / typecheck

```bash
uv run ruff check .
uv run ruff format --check .
uv run pyright
```

### Pre-commit hooks

Hooks are installed automatically via `pre-commit install` (run once after clone):

```bash
pre-commit install
pre-commit run --all-files
```

Hooks run: `ruff check` → `ruff format` → `pyright` → `pytest`.

---

## Data

Raw NASA FIRMS CSVs are cached under `data/raw/` (Amazon & Mekong AOIs, 2000–2026). Empirical results and publication figures live under `data/processed/` and `docs/figures/`. See `data/raw/fetch_manifest.json` for provenance.

---

## Testing

- `tests/test_harmonization_suite.py` — 7 tests covering the 5 core scientific equations.
- `tests/test_core_coverage.py` — 7 additional tests for previously untested public seams.
- `tests/test_ai_service_harness.py` — 22 tests verifying the Dual-System (System 1 + System 2) LangGraph harness, the Atomic / Domain Diagnostic tool tiers, Endpoint Profile resolution, citation grounding, human sign-off, the SSE event stream, and the absence of any ambient agent-tooling read.
- `tests/test_live_tdd_seams.py` — 5 live TDD vertical slice tests (marked `live`) verifying the native-chat adapters, the reasoning trace, the symbiosis escalation and the human sign-off gate against a real hosted model, real NASA FIRMS CSV harmonization, and live telemetry.

Run with:

```bash
uv run python -m pytest          # offline suite; no network, no provider spend
uv run python -m pytest -m live  # live suite; calls a hosted model and spends credit
```

The live suite is excluded from the default run and from continuous integration. It runs only from the manually triggered `Live Model Tests` workflow, so provider credit is spent only on request. Configure the credentials in the environment or in the workspace `.env` file:

```bash
export SYSTEM1_API_KEY=...   # System 1 classifier
export SYSTEM2_API_KEY=...   # System 2 deliberative layer
```

The whole benchmark can also be run against a real model, which writes its
measurements — tool rounds, clarifications, verification rejections, token
usage — to `data/processed/ai_harness_results_live.json`:

```bash
uv run python apps/ai-service/src/ai_service/run_all_usecases.py --live
```

The harness also exposes the run as a typed event stream, encodable as Server-Sent Events for a web client:

```python
from ai_service import FlareChronosDualSystemHarness, to_sse_frames

harness = FlareChronosDualSystemHarness(mode="live")
async for frame in to_sse_frames(
    harness.astream_use_case("UC-1.1 Why did Mekong detections jump in 2024?")
):
    ...  # bytes: b"event: node_completed\ndata: {...}\n\n"
```

---

## Linting, Formatting & Type Checking

- **Lint**: `ruff check` (rules configured via default ruff; see `pyproject.toml`)
- **Format**: `ruff format`
- **Type check**: `pyright` (basic mode, `pyrightconfig.json`)

All three are wired into pre-commit and CI.

---

## CI / CD

GitHub Actions workflow (`.github/workflows/ci.yml`):

- Matrix: Python 3.11 / 3.12 / 3.13 on Ubuntu
- Steps: `uv sync --group dev` → `ruff format --check` → `ruff check` → `pytest`
- Separate `typecheck` job running `pyright`

Branches are auto-deleted after merge.

---

## Domain Glossary & ADRs

- [`GLOSSARY.md`](GLOSSARY.md) / [`GLOSSARY-MAP.md`](GLOSSARY-MAP.md) — ubiquitous language (multi-context).
- [`docs/adr/`](docs/adr/) — Architecture Decision Records (0001–0008).
- [`docs/agents/`](docs/agents/) — agent skills config (issue tracker, triage labels, domain docs).
- [`docs/media/SOURCES.md`](docs/media/SOURCES.md) — editorial deliverable index, naming convention, and the rules that keep the pitch honest about the data.

---

## Contributing

1. Fork & create a feature branch.
2. Run `pre-commit install` and ensure `pre-commit run --all-files` passes.
3. Open a PR against `main`. CI must be green.

---

## License

MIT. See `LICENSE`.
