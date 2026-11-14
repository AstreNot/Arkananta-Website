# tools

- `build_site.py` writes `../index.html` from the content in the file and the numbers produced by the synthetic demos.
- `nivo/` renders the charts with Nivo (`@nivo/bar` 0.88.0, React 18.3.1) to static SVG at build time. Run `npm ci` in that folder first.
