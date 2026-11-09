'use client';

import { useEffect, useRef, useState } from 'react';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import { takeGlobeMorph, type GlobeMorphPayload } from '@/lib/globe/morph';

/** Carries the last globe frame into the Workbench map pane. */
export function GlobeMorph() {
  const pathname = usePathname();
  const [payload, setPayload] = useState<GlobeMorphPayload | null>(null);
  const [phase, setPhase] = useState<'start' | 'settle'>('start');
  const element = useRef<HTMLDivElement>(null);
  const consumed = useRef(false);
  const run = useRef({ frame: 0, timer: 0, attempts: 0 });

  useEffect(() => {
    if (pathname === '/') {
      consumed.current = false;
      return;
    }
    if (consumed.current || !pathname.startsWith('/workbench')) return;
    const frame = window.requestAnimationFrame(() => {
      const next = takeGlobeMorph();
      if (!next) return;
      consumed.current = true;
      setPayload(next);
      setPhase('start');
    });
    return () => window.cancelAnimationFrame(frame);
  }, [pathname]);

  useEffect(() => {
    if (!payload) return;
    const node = element.current;
    if (!node) return;

    node.style.setProperty('--morph-focus-x', `${payload.focusX * 100}%`);
    node.style.setProperty('--morph-focus-y', `${payload.focusY * 100}%`);

    run.current = { frame: 0, timer: 0, attempts: 0 };

    const settle = (target: HTMLElement | null) => {
      if (target) {
        const bounds = node.getBoundingClientRect();
        const rect = target.getBoundingClientRect();
        const left = rect.left - bounds.left;
        const top = rect.top - bounds.top;
        const right = bounds.right - rect.right;
        const bottom = bounds.bottom - rect.bottom;
        const scale = Math.max(rect.width / bounds.width, rect.height / bounds.height);
        const x = left + payload.focusX * rect.width - payload.focusX * bounds.width * scale;
        const y = top + payload.focusY * rect.height - payload.focusY * bounds.height * scale;
        node.style.setProperty('--morph-top', `${top}px`);
        node.style.setProperty('--morph-right', `${right}px`);
        node.style.setProperty('--morph-bottom', `${bottom}px`);
        node.style.setProperty('--morph-left', `${left}px`);
        node.style.setProperty('--morph-scale', `${scale}`);
        node.style.setProperty('--morph-x', `${x}px`);
        node.style.setProperty('--morph-y', `${y}px`);
      }
      setPhase('settle');
      run.current.timer = window.setTimeout(() => {
        setPayload(null);
        setPhase('start');
      }, 750);
    };

    const findTarget = () => {
      const target = document.querySelector<HTMLElement>('[data-tour="map"]');
      if (!target && run.current.attempts < 30) {
        run.current.attempts += 1;
        run.current.frame = window.requestAnimationFrame(findTarget);
        return;
      }
      settle(target);
    };

    run.current.frame = window.requestAnimationFrame(() => {
      run.current.frame = window.requestAnimationFrame(findTarget);
    });

    return () => {
      window.cancelAnimationFrame(run.current.frame);
      window.clearTimeout(run.current.timer);
    };
  }, [payload]);

  if (!payload) return null;

  return (
    <div ref={element} aria-hidden="true" className="fc-morph" data-phase={phase}>
      <Image src={payload.image} alt="" fill unoptimized sizes="100vw" className="fc-morph-image" />
    </div>
  );
}
