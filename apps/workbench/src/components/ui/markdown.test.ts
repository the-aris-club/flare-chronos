import { describe, expect, test } from 'bun:test';
import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { Markdown } from './markdown';

const html = (source: string) => renderToStaticMarkup(createElement(Markdown, null, source));

describe('Markdown', () => {
  test('renders the structure the models write', () => {
    const out = html(
      '### Report\n\n- **MODIS edge**: 9.6875 km² with `tool_a`\n- second\n\n1. one\n2. two',
    );

    expect(out).toContain('<h4');
    expect(out).toContain('Report');
    expect(out).toContain('<strong');
    expect(out).toContain('MODIS edge');
    expect(out).toContain('<code');
    expect(out).toContain('tool_a');
    expect(out).toContain('<ul');
    expect(out).toContain('<ol');
    expect(out).not.toContain('**');
    expect(out).not.toContain('###');
  });

  test('renders a GitHub table', () => {
    const out = html('| a | b |\n| - | - |\n| 1 | 2 |');

    expect(out).toContain('<table');
    expect(out).toContain('<th');
    expect(out).toContain('<td');
  });

  test('raw HTML from the model is shown as text, never as markup', () => {
    const out = html('<script>alert(1)</script><img src=x onerror=alert(1)> hello');

    expect(out).not.toContain('<script');
    expect(out).not.toContain('<img');
    expect(out).toContain('&lt;script&gt;');
    expect(out).toContain('hello');
  });

  test('a javascript: link is neutralised and a normal link opens safely', () => {
    const bad = html('[x](javascript:alert(1))');
    const good = html('[nasa](https://firms.modaps.eosdis.nasa.gov)');

    expect(bad).not.toContain('javascript:');
    expect(good).toContain('href="https://firms.modaps.eosdis.nasa.gov"');
    expect(good).toContain('rel="noopener noreferrer"');
    expect(good).toContain('target="_blank"');
  });

  test('images are not fetched from model output', () => {
    const out = html('![tracker](https://evil.example/pixel.png)');

    expect(out).not.toContain('<img');
    expect(out).not.toContain('evil.example/pixel.png"');
  });
});
