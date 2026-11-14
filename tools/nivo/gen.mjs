// Renders Nivo bar charts to static SVG strings (no client JS). stdin: JSON {id: spec}; stdout: JSON {id: svg}.
import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { Bar } from '@nivo/bar';

const h = React.createElement;
const FONT = "'JetBrains Mono',monospace";
const theme = {
  text: { fontFamily: FONT, fontSize: 12, fill: 'var(--muted)' },
  axis: { domain: { line: { stroke: 'transparent' } }, ticks: { line: { stroke: 'transparent' }, text: { fill: 'var(--muted)', fontSize: 12, fontFamily: FONT } } },
  grid: { line: { stroke: 'var(--line)' } },
  legends: { text: { fill: 'var(--muted)', fontSize: 12, fontFamily: FONT } },
  labels: { text: { fill: 'var(--fg)', fontSize: 12, fontFamily: FONT } },
};
const FMT = {
  pct: (v) => `${v.toFixed(1)}%`,
  int: (v) => `${Math.round(v)}`,
  money: (v) => Math.round(v).toLocaleString('en-US'),
};
const textStyle = { fill: 'var(--fg)', fontSize: 12, fontFamily: FONT, fontVariantNumeric: 'tabular-nums' };

function responsive(svg) {
  return svg.replace(/<svg([^>]*?) width="(\d+)" height="(\d+)"/, '<svg$1 viewBox="0 0 $2 $3" class="svg"');
}

function hbar(s) {
  const W = 260;
  const H = s.rows.length * 26 + (s.ref ? 18 : 6);
  const labelLayer = ({ bars }) =>
    h('g', null, bars.map((b) =>
      h('text', { key: b.key, x: b.x + b.width + 6, y: b.y + b.height / 2, dominantBaseline: 'central', style: textStyle },
        FMT[s.format](b.data.data.value))));
  const markers = s.ref ? [{
    axis: 'x', value: s.ref.value, legend: s.ref.label, legendPosition: 'bottom', legendOrientation: 'horizontal',
    lineStyle: { stroke: 'var(--muted)', strokeDasharray: '3 3' }, textStyle: { fill: 'var(--muted)', fontSize: 12, fontFamily: FONT },
  }] : undefined;
  return responsive(renderToStaticMarkup(h(Bar, {
    width: W, height: H, data: s.rows, keys: ['value'], indexBy: 'label', layout: 'horizontal',
    margin: { top: 3, right: 58, bottom: s.ref ? 18 : 3, left: 100 }, padding: 0.3, minValue: 0, maxValue: s.max,
    colors: (b) => (b.data.series ? 'var(--c2)' : 'var(--c1)'), theme,
    axisLeft: { tickSize: 0, tickPadding: 8 }, axisBottom: null, enableGridY: false, enableLabel: false,
    layers: ['grid', 'axes', 'bars', labelLayer, 'markers'], markers,
    isInteractive: false, animate: false, role: 'img', ariaLabel: s.aria, borderRadius: 2,
  })));
}

function stack(s) {
  const W = 260, H = 136;
  const totals = Object.fromEntries(s.data.map((r) => [r.year, s.keys.reduce((a, k) => a + r[k], 0)]));
  const totalLayer = ({ xScale, yScale }) =>
    h('g', null, s.data.map((r) =>
      h('text', { key: r.year, x: xScale(r.year) + xScale.bandwidth() / 2, y: yScale(totals[r.year]) - 5, textAnchor: 'middle', style: textStyle }, totals[r.year])));
  return responsive(renderToStaticMarkup(h(Bar, {
    width: W, height: H, data: s.data, keys: s.keys, indexBy: 'year', groupMode: 'stacked', layout: 'vertical',
    margin: { top: 18, right: 6, bottom: 52, left: 6 }, padding: 0.3, minValue: 0, maxValue: s.max,
    colors: ({ id }) => (id === s.keys[0] ? 'var(--c2)' : 'var(--c1)'), theme,
    axisBottom: { tickSize: 0, tickPadding: 6 }, axisLeft: null, enableGridY: false, enableLabel: false,
    layers: ['grid', 'axes', 'bars', totalLayer, 'legends'],
    legends: [{ dataFrom: 'keys', anchor: 'bottom-left', direction: 'row', translateY: 50, itemWidth: 70, itemHeight: 14, itemsSpacing: 6, symbolSize: 10 }],
    isInteractive: false, animate: false, role: 'img', ariaLabel: s.aria, borderRadius: 2,
  })));
}

const input = JSON.parse(await new Promise((res) => { let b = ''; process.stdin.on('data', (c) => (b += c)); process.stdin.on('end', () => res(b)); }));
const out = {};
for (const [id, s] of Object.entries(input)) out[id] = s.type === 'stack' ? stack(s) : hbar(s);
process.stdout.write(JSON.stringify(out));
