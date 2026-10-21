# Editorial Sources Index

The repository holds the **science**. The rendered **story** lives outside it.

This file is the index for the editorial deliverables described in
[`docs/05_Pitch_Deck_and_Video_Script.md`](../05_Pitch_Deck_and_Video_Script.md)
and the glossary terms **Main Submission Video** and **Fast Pitch** in
[`GLOSSARY.md`](../../GLOSSARY.md).

## Why nothing binary is committed

`data/raw/` already commits ~124 MB of NASA FIRMS CSV slices, which is
acceptable because they are the reproducibility substrate. Editorial
sources do not qualify:

- an After Effects / Blender project is multi-gigabyte, binary, and
  diff-hostile;
- rendered masters are reproducible from those sources, so committing
  both stores the same content twice;
- Git LFS is not configured in this repository.

So: **sources stay in external storage, renders ship as GitHub
Releases, and the repository keeps only what text can express** — the
script, the shot list, the storyboard, and the figures the code
generates.

## Deliverables

| Deliverable | Release tag | Source | Notes |
|---|---|---|---|
| Main Submission Video (120 s, EN) | `v0.1.0` | external storage | Primary NASA Space Apps submission |
| Main Submission Video (120 s, VI) | `v0.1.0` | external storage | Separate cut, separate timing |
| Fast Pitch (30 s, EN) | `v0.1.0` | external storage | Reserved in `docs/05` §3 — **not yet written** |
| Pitch Deck (7 slides) | `v0.1.0` | external storage | Mirrors `docs/05` §2 blueprint |

## Naming convention

Use the same slug everywhere — source project, render, release asset:

```
flare-chronos-<artifact>-<variant>-<version>.<ext>
```

| Artifact | Slug | Example |
|---|---|---|
| Main Submission Video | `main-video` | `flare-chronos-main-video-en-v0.1.0.mp4` |
| Fast Pitch | `fast-pitch` | `flare-chronos-fast-pitch-en-v0.1.0.mp4` |
| Pitch Deck | `pitch-deck` | `flare-chronos-pitch-deck-v0.1.0.pdf` |
| Narrative Asset | `asset-<subject>` | `flare-chronos-asset-footprint-ellipse-v0.1.0.mov` |

`en` / `vi` denote the voiceover language. A variant with no voiceover
uses `mute`.

## Source locations

Fill this in once the external storage exists. One row per source
project, with a link a collaborator can open.

| Source project | Editor | Location | Last synced |
|---|---|---|---|
| _TBD_ | _TBD_ | _TBD_ | _TBD_ |

## Rules

1. **Scientific Figures are never edited by hand.** The five charts in
   `docs/figures/` are rendered by `apps/benchmark-cli/src/benchmark_cli/figure_renderer.py`
   from `data/processed/empirical_results.json`. If a figure needs to
   change, change the code and re-run
   `uv run python -m benchmark_cli.run_experiments`.
2. **Narrative Assets never impersonate measurements.** Anything
   hand-authored is a Narrative Asset and carries that framing on screen.
3. **Every number on screen is checked.** The published metrics live in
   `data/processed/empirical_results.json` and are guarded by
   `tests/test_documented_claims_consistency.py`. Read the numbers off
   that artifact, not off an older document.
4. **Vietnamese decimal convention.** The documents write `1.324,2%` to
   mean 1,324.2% (dot = thousands separator, comma = decimal). English
   title cards must use `1,324.2%` — a bare `1.324%` reads as 1.3%.
