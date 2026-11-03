import {
  ArrowLeft,
  ArrowRight,
  ArrowUpRight,
  Check,
  ChevronDown,
  ChevronRight,
  CircleCheck,
  CircleDot,
  CircleX,
  ClipboardCheck,
  Clock,
  Contrast,
  Download,
  FileText,
  Globe,
  History,
  Languages,
  Maximize2,
  Menu,
  MessagesSquare,
  Pause,
  Search,
  Minus,
  Play,
  Plus,
  RefreshCw,
  SlidersHorizontal,
  TriangleAlert,
  X,
  type LucideIcon,
} from 'lucide-react';

export const ICON = {
  theme: Contrast,
  language: Languages,
  external: ArrowUpRight,
  alert: TriangleAlert,
  close: X,
  chevron: ChevronDown,
  tour: Play,
  evidence: FileText,
  briefing: MessagesSquare,
  pause: Pause,
  service: CircleDot,
  dot: CircleDot,
  check: Check,
  plus: Plus,
  minus: Minus,
  reset: Maximize2,
  menu: Menu,
  globe: Globe,
  arrow: ArrowRight,
  back: ArrowLeft,
  next: ChevronRight,
  review: ClipboardCheck,
  audit: History,
  search: Search,
  filter: SlidersHorizontal,
  download: Download,
  clock: Clock,
  checkCircle: CircleCheck,
  xCircle: CircleX,
  rewrite: RefreshCw,
} as const;

const SIZES = {
  xs: 10,
  sm: 14,
  md: 16,
  lg: 20,
} as const;

type AmIconProps = {
  icon: LucideIcon;
  size?: keyof typeof SIZES;
  className?: string;
};

export function AmIcon({ icon: Glyph, size = 'md', className }: AmIconProps) {
  return (
    <Glyph
      aria-hidden="true"
      focusable="false"
      size={SIZES[size]}
      strokeWidth={2}
      className={className}
    />
  );
}
