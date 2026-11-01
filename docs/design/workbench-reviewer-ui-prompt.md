# Prompt for Claude Design — Reviewer Screens (addendum)

Paste this after the Workbench prompt. Extend the existing design; keep the visual system, logo, typography and colours. This addendum covers only the reviewer-facing screens. Do not restate or redesign the map, calendar, clock or comparator.

## Goal

The agent run is finished or paused. A reviewer must find the result, understand what it proposes, inspect the evidence, decide, and see the record.

Add a `Review` tab in the Workbench header with a badge for items waiting. The existing Briefing & Sign-off panel stays as the run summary; the new screens carry the review work.

## Screens

### 1. Review queue

A dense table, not a dashboard.

- Tabs: Needs decision (default), Published, Withheld.
- Columns: run, use case, region, period, proposed action, status, owner, reviewer, waiting time, updated.
- Filters: region, use case, urgency, owner, assigned to me.
- Row opens Review run.
- Empty: "No runs waiting for a decision."
- Error: service unavailable, no permission, expired session — with a clear action, no fake rows.

No bulk approve.

### 2. Review run

Desktop: three columns; right rail sticky.

**Left — What is being authorized:**

- Proposed action card in plain language.
- Region and period, with a map thumbnail if the action is spatial.
- Threshold card: SFAI value, display threshold `+2.2σ`, crisis threshold `+2.5σ`, clearly separated.
- Evidence status: measured epoch or interpolated year; observed or modelled cell.
- Provenance: owner, classifier confidence source, System 1 / System 2 model names, service health, duration.

**Centre — Full briefing:**

- Audience switch: Rangers / Forestry leaders / Climate scientists.
- Full text, no truncation; scrolls inside the column.
- Each number is a citation chip: verified, rewritten, no source.
- Chip opens Citation detail.
- Optional "show citation keys" toggle.

**Right — Decision rail:**

- Evidence summary: numbers verified, numbers without source, citation issues, self-corrections, synthesis source.
- Decision basis checklist, each item pass/fail: action stated; every number verified; no citation issues; no missing sources; threshold and epoch valid; service healthy; reviewer is owner or approver.
- Reviewer block: name, role, owner/approver, UTC time.
- Decision form: Approve / Reject, required reason code, optional note.
- Approve unavailable when any basis item fails; show why. Reject always available.
- After decision: outcome and audit id.

**Bottom — Run timeline**, collapsed: classify → tool calls → reasoning → verification → approval → briefing. Expand for details. Show the reasoning summary only, never hidden chain-of-thought.

### 3. Briefing dialog

Opens from `View full briefing`.

- Header: run, use case, region, Published or Withheld, audience switch.
- Stakeholder header: audience tier, cognitive path, System 1 / System 2 models, synthesis source.
- Full briefing.
- Verification table: value, unit, source tool, source field, status, verdict.
- Each row opens Citation detail.
- Decision record: decision, reviewer, role, UTC time, reason, note, audit id.
- Published: "Released to … Signed by …".
- Withheld: "Nothing was released. The decision was recorded." No briefing text.
- Copy run id and audit id.

### 4. Citation detail

Popover on desktop, bottom sheet on mobile.

- Sentence with the number highlighted.
- Rendered value and unit.
- Fact key in monospace.
- Source tool.
- Raw value.
- Provenance tag.
- Verdict: verified, rewritten, no source; tolerance if relevant.
- Rewritten: rejected value, accepted value, verifier note.
- Link to the tool call.

Never show an empty source tool as normal; mark it as blocking.

### 5. Decision confirmation

Last checkpoint.

- Restate run, action, decision, reason, reviewer.
- Approve: "This releases the briefing and authorizes the field action."
- Reject: "Nothing will be released. The decision is recorded and cannot be edited."
- Blocking evidence: show the list, keep Approve unavailable, offer Reject or Re-run.
- Buttons: Confirm approval / Confirm rejection / Cancel.
- After: outcome, audit id, link to the result.

Reason codes: evidence confirmed, stale data, duplicate alert, evidence conflict, outside authority, service degraded, other. Other requires a note.

### 6. Audit trail

- Read-only table: UTC time, run, reviewer, role, decision, reason, note, audit id.
- Filters: reviewer, decision, date, use case.
- Export CSV and JSON.
- Row opens the result.
- No edit, delete or undo controls.

### 7. Empty and error screens

Design: loading, empty queue, expired session, no permission, service unavailable, degraded service, failed run, waiting for decision, clarification requested, published, withheld, superseded.

## Content rules

- No approval without evidence.
- No approval without a reason.
- No bulk or automatic approval.
- Decisions are read-only; a correction is a new run.
- Withheld shows no briefing text.
- Published requires a recorded decision.
- Every number shows a status.
- Audience switch changes language, not numbers.
- No invented reviewer names or audit ids.
- No countdown pressure.
- Never colour alone.

## Visual

- Reuse the Workbench palette: space blue-black, amber-red fire, teal harmonized, cyan anomaly outline, purple/grey filtered.
- Denser and calmer than the map: tables, chips, sticky rail, restrained motion.
- Tabular numerals; monospace for fact keys, tools, audit ids.
- Status words: Needs decision, Waiting, Published, Withheld, Failed, Stale, Degraded.
- Dark and light themes; contrast 4.5:1; keyboard focus visible.

## Sample content

Use these for the mock; keep the "synthetic data except published figures" banner.

**Run A — UC-S1.4, Mekong 2026:** 1,842 NRT detections (MODIS 312, SNPP 604, NOAA-20 512, NOAA-21 414), 815 episodes, Ω 2.0975, SFAI `+2.61σ` vs `+2.5σ` crisis, 9/9 verified, 1 self-correction. Approved by Nguyễn Thi Mai, approver, `2026-10-31T16:02:58Z`, reason evidence confirmed, audit `A-0195`. Action: Tier-1 flash alert, 24 hours.

**Run B — UC-2.2, Mekong 2024:** MODIS edge `9.69 km²`, scan `4.83 km`, track `2.01 km`, 13 H3 Res 8 cells, VIIRS `0.138 km²`, `74.23×` reduction, 25-minute revisit, 95-minute clustering. Action: dispatch two teams to the H3 cells at the next overpass.

**Run C — Withheld:** same proposal, rejected by Trần Văn An, duplicate alert, "Already alerted at 09:12 UTC." No briefing text; record visible.

## Bilingual labels

Use the existing EN/VI switch. Key terms: Review = Xem xét; Review queue = Hàng chờ xem xét; Needs decision = Cần quyết định; Published = Đã phát hành; Withheld = Không phát hành; Proposed action = Hành động đề xuất; Decision basis = Căn cứ quyết định; Verification table = Bảng kiểm chứng; Citation detail = Chi tiết trích dẫn; Approve = Phê duyệt; Reject = Từ chối; Reason = Lý do; Audit trail = Nhật ký phê duyệt; Audit id = Mã nhật ký; Degradation tier = Cấp suy giảm.

## Deliverables

- Review queue, Review run, Briefing dialog (published and withheld), Citation detail, Decision confirmation, Audit trail.
- Empty and error screens.
- Dark and light; desktop 1440×900; tablet and mobile for the queue, run, dialog and decision.
- Component sheet: queue row, status chip, decision-basis item, citation chip, citation row, source-tool badge, decision card, reason select, audit row, outcome banner.
- Interaction notes: queue → run → citation → confirmation → result; sticky rail; focus order.

## Avoid

- A review screen that hides the evidence.
- Approve available when evidence is incomplete.
- A summary instead of the full text at the decision point.
- Approval without seeing the proposed action.
- Reject hidden or secondary.
- Fake queue rows.
- Replay or recorded runs presented as live.
- A dialog that cannot be reopened.
