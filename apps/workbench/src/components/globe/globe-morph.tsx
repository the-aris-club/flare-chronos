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

    const frame = window.requestAnimationFrame(() => {
      window.requestAnimationFrame(() => {
        const target = document.querySelector<HTMLElement>('[data-tour="map"]');
        if (target) {
          const rect = target.getBoundingClientRect();
          node.style.setProperty('--morph-top', `${rect.top}px`);
          node.style.setProperty('--morph-left', `${rect.left}px`);
          node.style.setProperty('--morph-width', `${rect.width}px`);
          node.style.setProperty('--morph-height', `${rect.height}px`);
        }
        setPhase('settle');
      });
    });

    const timer = window.setTimeout(() => {
      setPayload(null);
      setPhase('start');
    }, 1150);

    return () => {
      window.cancelAnimationFrame(frame);
      window.clearTimeout(timer);
    };
  }, [payload]);

  if (!payload) return null;

  return (
    <div ref={element} aria-hidden="true" className="fc-morph" data-phase={phase}>
      <Image src={payload.image} alt="" fill unoptimized sizes="100vw" className="fc-morph-image" />
    </div>
  );
}
