Arkananta Portfolio

A single static page (index.html) with a light/dark theme. No client-side frameworks.

index.html is generated, do not edit it by hand:
  cd tools/nivo && npm ci
  python tools/build_site.py
The build runs the synthetic demo projects (folder portfolio-demos next to this repo, or set PORTFOLIO_DEMOS),
draws the charts with Nivo (@nivo/bar) as static SVG, and writes index.html.
Content (experience, project text, links) lives at the top of tools/build_site.py.
