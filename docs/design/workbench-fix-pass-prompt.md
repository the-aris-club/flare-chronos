# Prompt for Claude Design — Fix Pass on the Existing Flare-Chronos Design

Apply these corrections to the existing Flare-Chronos Workbench and Review design. Do not redesign the product. Keep the layout, palette, typography, logo, sample data and all existing screens. Change only the items below.

Paste this after the original Workbench prompt, or use it as the correction brief for the existing project.

---

## 1. Review queue

At 1440 × 900 the table must show all ten columns, including `UPDATED`, without clipping the right edge.

- Columns: run, use case, region, period, proposed action, status, owner, reviewer, waiting time, updated.
- Keep the current dense table styling and the status chips with glyph + word.
- Allow horizontal scrolling only below 1280 px.
- Do not add bulk selection or bulk approval.

## 2. Review run — left column

The three threshold cards currently collide at 1440 px because the left column is too narrow.

- Make `SFAI value` one full-width row: label on the left, value on the right.
- Put `Display threshold` and `Crisis threshold` side by side below it.
- Keep the +2.2σ dashed cyan border and the +2.5σ solid red border.
- Keep the proposed action card and the map thumbnail unchanged.

## 3. Review run — right rail

- `Synthesis source` must wrap inside the rail; it must never be clipped at the right edge.
- Use a two-column label/value layout that lets the value wrap to a second line.
- Keep the Decision Basis checklist and the reviewer block as they are.
- The decision form may scroll with the rail; do not shrink the basis items to force it above the fold.

## 4. Withheld run

When the decision is Reject, the run timeline must not show ✓ for `Approval` or `Briefing`.

- Use ⊘ in purple for both steps.
- Keep the semantics: `Approval` = rejected, `Briefing` = withheld.
- The briefing body stays hidden; only the decision record is visible.
- The outcome banner remains `Withheld` with “Nothing was released. The decision was recorded.”

## 5. Decision records and audit IDs

Use one audit ID series across the Workbench and Review samples:

- `A-0193` — Workbench published sample, run R-0412, reason “Evidence confirmed”.
- `A-0194` — RUN-C, rejected for “Duplicate alert”.
- `A-0195` — RUN-A, approved for “Evidence confirmed”.
- `A-0196` — the new decision created in the demo.

Replace the placeholders “Issued by the decision service”, “Issued by service” and “Not in sample data” with the matching sample audit ID.

Use full UTC ISO timestamps, for example `2026-10-31T16:02:58Z`. The decision record must show: decision, reviewer, role, UTC time, reason code, note, audit id.

## 6. Workbench sign-off card

- A reason is required for **both** Approve and Reject. Label the field `Reason · required`.
- Approve must not publish with an empty reason. Show the inline error “Add a reason before deciding.”
- Replace `D-0xxx` decision IDs with `A-0xxx`. After an approval, show `decision A-0196`.
- The published sample must show `A-0193` and the reason “Evidence confirmed”. Remove “No reason given”.
- Keep the compact Workbench panel. The full evidence and Decision Basis live in the Review screen.

## 7. Screens canvas

Add a `Review` group to the Screens canvas with six frames in dark and light:

1. Review queue — `view=queue`
2. Review run — `view=run&run=B`
3. Briefing dialog — `view=run&run=A&overlay=briefing`
4. Decision confirmation — `view=run&run=B&overlay=confirm`
5. Citation detail — `view=run&run=B&overlay=citation`
6. Audit trail — `view=audit`

Keep the existing Workbench, tablet and mobile groups unchanged. Use the same frame scale and `Open ↗` link pattern.

## 8. Vietnamese labels

When the language switch is VI, translate the reviewer chrome. Do not change the English briefing body; the existing note already explains that the model writes in English.

- Decision Basis: `ĐẠT` / `KHÔNG ĐẠT`; details such as `8/8 đã xác minh · 1 sau tự sửa`, `Đã nêu rõ ở cột bên trái`, `Không tìm thấy`, `Mọi con số đều truy được về một lệnh gọi tool`, `Kỳ đo thực tế 2024 · UC-2.2 không dùng SFAI`, `Tier 0 · dịch vụ đầy đủ`, `Nguyễn Thị Mai · chủ sở hữu và người phê duyệt`.
- Provenance labels: `Bộ phân loại`, `Dịch vụ`, `Thời lượng`; service values `✓ Tier 0 · hoạt động tốt`.
- Reviewer block: `Người phê duyệt · chủ sở hữu`; time `Bây giờ · …`.
- Timeline titles: `Phân loại`, `Gọi tool`, `Suy luận`, `Kiểm chứng`, `Phê duyệt`, `Bản tin`.
- Approval line: `Đã phê duyệt bởi …`; rejected line: `Đã từ chối bởi …`.
- Do not translate tool names, model ids, fact keys, units, or audit ids.

## 9. Consistency rules

- This is one review surface, not a set of switchable variations.
- Keep the design visual only; no backend behaviour or data-contract language.
- Use the designed empty, error and unavailable states; never draw fake rows.
- Status always pairs a glyph and a word with colour; never colour alone.
- No countdowns or urgency timers.
- Keep the prototype banner “Prototype · synthetic data except published figures”.

## Deliverables

- Updated Review queue, Review run, Withheld run, Workbench briefing and published screens.
- Updated Screens canvas with the Review group.
- Updated component sheet showing the fixed threshold layout, the wrapped Synthesis source, the withheld timeline and the complete decision record.
- Dark and light at 1440 × 900; tablet and mobile for queue, run, dialog and decision.
