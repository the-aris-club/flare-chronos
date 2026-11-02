import type { ComponentProps } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

type Tag<K extends keyof React.JSX.IntrinsicElements> = Omit<ComponentProps<K>, 'node'> & {
  node?: unknown;
};

function strip<T extends { node?: unknown }>({ node: _node, ...rest }: T): Omit<T, 'node'> {
  return rest;
}

/**
 * Renders model-written Markdown. The text is untrusted, so raw HTML stays disabled (it is
 * shown as text), images are never fetched, and links open in a new tab without a referrer.
 * `react-markdown` also drops `javascript:` and other unsafe URL protocols by default.
 */
export function Markdown({ children }: { children: string }) {
  return (
    <div className="text-body flex min-w-0 flex-col gap-2 leading-relaxed break-words">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        disallowedElements={['img']}
        components={{
          h1: (props: Tag<'h1'>) => (
            <h3 {...strip(props)} className="text-subhead mt-1 font-semibold" />
          ),
          h2: (props: Tag<'h2'>) => (
            <h3 {...strip(props)} className="text-subhead mt-1 font-semibold" />
          ),
          h3: (props: Tag<'h3'>) => (
            <h4 {...strip(props)} className="text-body mt-1 font-semibold" />
          ),
          h4: (props: Tag<'h4'>) => <h5 {...strip(props)} className="text-body font-semibold" />,
          ul: (props: Tag<'ul'>) => <ul {...strip(props)} className="ml-5 list-disc space-y-1" />,
          ol: (props: Tag<'ol'>) => (
            <ol {...strip(props)} className="ml-5 list-decimal space-y-1" />
          ),
          strong: (props: Tag<'strong'>) => (
            <strong {...strip(props)} className="text-ink font-semibold" />
          ),
          code: (props: Tag<'code'>) => (
            <code {...strip(props)} className="bg-raised text-meta rounded-sm px-1 font-mono" />
          ),
          pre: (props: Tag<'pre'>) => (
            <pre
              {...strip(props)}
              className="bg-raised text-meta overflow-x-auto rounded-md p-2 font-mono"
            />
          ),
          blockquote: (props: Tag<'blockquote'>) => (
            <blockquote {...strip(props)} className="border-line text-ink-muted border-l-2 pl-3" />
          ),
          a: (props: Tag<'a'>) => (
            <a
              {...strip(props)}
              target="_blank"
              rel="noopener noreferrer"
              className="text-cyan underline underline-offset-2"
            />
          ),
          table: (props: Tag<'table'>) => (
            <div className="border-line overflow-x-auto rounded-md border">
              <table {...strip(props)} className="w-full border-collapse text-left" />
            </div>
          ),
          th: (props: Tag<'th'>) => (
            <th
              {...strip(props)}
              className="bg-raised text-meta border-line border-b px-2.5 py-1.5 font-semibold"
            />
          ),
          td: (props: Tag<'td'>) => (
            <td
              {...strip(props)}
              className="text-meta border-line border-b px-2.5 py-1.5 last:border-0"
            />
          ),
        }}
      >
        {children}
      </ReactMarkdown>
    </div>
  );
}
