'use client';

import { useCallback, forwardRef, useEffect, useImperativeHandle, useRef, useState } from 'react';
import { useLocale, useTranslations } from 'next-intl';
import type { RegionId } from '@/lib/calendar/types';
import { GLOBE_DATA } from '@/lib/globe/data';
import { saveGlobeMorph } from '@/lib/globe/morph';
import { GlobeScene } from '@/lib/globe/scene';
import type { BootStep, GlobeHandle } from '@/lib/globe/types';
import { GlobeFallback } from './globe-fallback';

const GLOBE_PATHS = {
  land: GLOBE_DATA.land,
  borders: GLOBE_DATA.borders,
  graticule: GLOBE_DATA.graticule,
  mekong: GLOBE_DATA.regions.mekong.coverage,
  amazon: GLOBE_DATA.regions.amazon.coverage,
};

export type GlobeLabel = {
  id: RegionId;
  name: string;
  measured: number[];
  yearStart: number;
  total: number;
};

type GlobeCanvasProps = {
  labels: GlobeLabel[];
  theme: 'dark' | 'light';
  hovered: RegionId | null;
  onHover: (region: RegionId | null) => void;
  onSelect: (region: RegionId) => void;
  onArrive: (region: RegionId) => void;
  onProgress: (step: BootStep) => void;
};

export const GlobeCanvas = forwardRef<GlobeHandle, GlobeCanvasProps>(
  function GlobeCanvas(props, ref) {
    const t = useTranslations('Globe');
    const locale = useLocale();
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const sceneRef = useRef<GlobeScene | null>(null);
    const labelRefs = useRef<Partial<Record<RegionId, HTMLDivElement | null>>>({});
    const propsRef = useRef(props);
    const [failed, setFailed] = useState(false);

    const setLabelRef = useCallback(
      (id: RegionId) => (element: HTMLDivElement | null) => {
        labelRefs.current[id] = element;
      },
      [],
    );

    useEffect(() => {
      if (!canvasRef.current) return;
      const media = window.matchMedia('(prefers-reduced-motion: reduce)');

      try {
        sceneRef.current = new GlobeScene({
          canvas: canvasRef.current,
          labels: labelRefs.current,
          theme: propsRef.current.theme,
          reducedMotion: media.matches,
          onProgress: (step) => propsRef.current.onProgress(step),
          onHover: (region) => propsRef.current.onHover(region),
          onSelect: (region) => propsRef.current.onSelect(region),
          onArrive: (region) => {
            const image = sceneRef.current?.snapshot();
            const canvas = canvasRef.current;
            if (image && canvas) {
              const bounds = canvas.getBoundingClientRect();
              const label = labelRefs.current[region]?.getBoundingClientRect();
              saveGlobeMorph({
                image,
                focusX: label ? (label.left + label.width / 2 - bounds.left) / bounds.width : 0.5,
                focusY: label ? (label.top + label.height / 2 - bounds.top) / bounds.height : 0.5,
              });
            }
            propsRef.current.onArrive(region);
          },
        });
      } catch {
        window.setTimeout(() => setFailed(true), 0);
        propsRef.current.onProgress('borders');
        propsRef.current.onProgress('photo');
      }

      const observer = new ResizeObserver(() => sceneRef.current?.resize());
      observer.observe(canvasRef.current);

      return () => {
        observer.disconnect();
        sceneRef.current?.dispose();
        sceneRef.current = null;
      };
    }, []);

    useEffect(() => {
      sceneRef.current?.setTheme(props.theme);
    }, [props.theme]);

    useEffect(() => {
      sceneRef.current?.setHighlight(props.hovered);
    }, [props.hovered]);

    useImperativeHandle(
      ref,
      () => ({
        flyTo: (region) => sceneRef.current?.flyTo(region) ?? false,
        highlight: (region) => sceneRef.current?.setHighlight(region),
        peek: (region) => sceneRef.current?.peek(region),
        snapshot: () => sceneRef.current?.snapshot() ?? null,
      }),
      [],
    );

    return (
      <div className="absolute inset-0 overflow-hidden">
        <canvas
          ref={canvasRef}
          role="img"
          aria-label={t('canvasLabel')}
          className={`size-full touch-none ${props.hovered ? 'cursor-pointer' : 'cursor-grab'}`}
        />

        {!failed &&
          props.labels.map((label) => (
            <div
              key={`${label.id}-${locale}`}
              ref={setLabelRef(label.id)}
              aria-hidden="true"
              className="fc-globe-label"
            >
              <span className="fc-globe-pin" />
              <b>{label.name}</b>
              <span className="text-micro text-ink-subtle font-mono">
                {label.measured.length}/{label.total}
              </span>
              {props.hovered === label.id && (
                <span className="fc-globe-tooltip">
                  <span className="flex gap-0.5">
                    {Array.from({ length: label.total }, (_, index) => label.yearStart + index).map(
                      (year) => (
                        <span
                          key={year}
                          className={`h-2 flex-1 rounded-xs ${
                            label.measured.includes(year) ? 'bg-ink' : 'border-line-strong border'
                          }`}
                        />
                      ),
                    )}
                  </span>
                  <span className="text-micro text-ink-muted mt-1 block">{t('openHint')}</span>
                </span>
              )}
            </div>
          ))}
        {failed && <GlobeFallback label={t('fallback')} paths={GLOBE_PATHS} />}
      </div>
    );
  },
);
