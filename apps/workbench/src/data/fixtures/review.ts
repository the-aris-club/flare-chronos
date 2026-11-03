// TODO(api): review runs — replace this fixture with GET /api/v1/review/runs,
// GET /api/v1/review/runs/:id, and the decision/audit endpoints.
// The shape mirrors Flare-Chronos Review.dc.html RUNS / INIT_DEC.

export type Audience = 'rangers' | 'leaders' | 'scientists';
export type FactVerdict = 'verified' | 'rewritten' | 'nosource';
export type DecisionKind = 'approve' | 'reject';
export type RunStatus = 'needs' | 'published' | 'withheld';

export type Fact = {
  key: string;
  value: string;
  unit: string;
  text: string;
  tool: string;
  field: string;
  raw: string;
  provenance: string;
  tolerance: string;
  call: string;
  verdict: FactVerdict;
  rejected?: string;
  note?: string;
};

export type ToolCall = {
  id: string;
  name: string;
  fields: string;
  time: string;
};

export type ReviewRun = {
  id: string;
  useCase: string;
  useCaseName: { en: string; vi: string };
  region: { en: string; vi: string };
  period: { en: string; vi: string };
  urgency: 'crisis' | 'elevated';
  spatial: boolean;
  action: { en: string; vi: string };
  scope: { en: string; vi: string };
  sfai: string;
  thresholdNote: { en: string; vi: string };
  epoch: { en: string; vi: string };
  cellLabel: { en: string; vi: string };
  classifier: string;
  duration: string;
  owner: string;
  assignee: string;
  updated: string;
  waitingSince: string;
  facts: Record<string, Fact>;
  brief: Record<Audience, string[]>;
  tools: ToolCall[];
  verification: string;
};

export type Decision = {
  kind: DecisionKind;
  reviewer: string;
  role: string;
  at: string;
  reason: string;
  note: string;
  audit: string;
};

export const PRINCIPAL = {
  name: 'Nguyễn Thị Mai',
  initials: 'NM',
  email: 'mai.nguyen@vnfp.gov.vn',
  role: 'Approver',
  expires: '01/11/2026 · 18:00 UTC',
};

export const INITIAL_DECISIONS: Record<string, Decision> = {
  'RUN-0411': {
    kind: 'approve',
    reviewer: PRINCIPAL.name,
    role: PRINCIPAL.role,
    at: '2026-10-31T16:02:58Z',
    reason: 'evidence',
    note: '',
    audit: 'A-0195',
  },
  'RUN-0413': {
    kind: 'reject',
    reviewer: 'Trần Văn An',
    role: 'Approver',
    at: '2026-10-31T15:18:44Z',
    reason: 'duplicate',
    note: 'Already alerted at 09:12 UTC.',
    audit: 'A-0194',
  },
};

export const REASONS = [
  { value: 'evidence', en: 'Evidence confirmed', vi: 'Dữ liệu kiểm chứng đã xác nhận' },
  { value: 'stale', en: 'Stale data', vi: 'Dữ liệu lỗi thời' },
  { value: 'duplicate', en: 'Duplicate alert', vi: 'Cảnh báo trùng lặp' },
  { value: 'conflict', en: 'Evidence conflict', vi: 'Dữ liệu kiểm chứng mâu thuẫn' },
  { value: 'authority', en: 'Outside authority', vi: 'Ngoài thẩm quyền' },
  { value: 'degraded', en: 'Service degraded', vi: 'Dịch vụ suy giảm' },
  { value: 'other', en: 'Other', vi: 'Khác' },
];

export const AUDIENCES = [
  {
    value: 'rangers',
    en: 'Rangers',
    vi: 'Kiểm lâm',
    roleEn: 'Field operations',
    roleVi: 'Vận hành thực địa',
  },
  {
    value: 'leaders',
    en: 'Forestry leaders',
    vi: 'Lãnh đạo lâm nghiệp',
    roleEn: 'Decision makers',
    roleVi: 'Người ra quyết định',
  },
  {
    value: 'scientists',
    en: 'Climate scientists',
    vi: 'Nhà khoa học khí hậu',
    roleEn: 'Technical',
    roleVi: 'Kỹ thuật',
  },
] as const;
export function statusOf(id: string, decisions: Record<string, Decision>): RunStatus {
  const decision = decisions[id];
  if (!decision) return 'needs';
  return decision.kind === 'approve' ? 'published' : 'withheld';
}

export function factText(template: string, facts: Record<string, Fact>): string {
  return template.replace(/\{(\w+)\}/g, (_, key: string) => facts[key]?.text ?? `{${key}}`);
}
