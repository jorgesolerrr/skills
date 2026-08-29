# Drawing a blueprint figure in SVG

Distilled from [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) (MIT) to what a blueprint figure needs. Read this once, then the file for the figure's type.

Every figure is one inline `<svg>` inside a `<figure>` in `BLUEPRINT.html`. No external image, no script.

## Tokens

Colors and fonts are CSS variables declared once in the page `<style>` (see [`../template.html`](../template.html)). SVG attributes reference them: `fill="var(--ink)"`, `stroke="var(--muted)"`. A hex value inside an `<svg>` is a bug.

| Variable | Role in a figure |
|---|---|
| `--paper` | page background, node fill, label masks |
| `--ink` | node stroke, primary text |
| `--muted` | default arrow stroke, secondary text |
| `--soft` | sublabels, arrow labels |
| `--rule` | hairlines, lifelines, frame borders |
| `--accent` | the 1 or 2 focal elements of a figure, and nothing else |
| `--accent-tint` | fill of an accent-stroked node |
| `--link` | arrows that cross a process or network boundary |
| `--new` | stroke of a node the feature adds |

When the repo already declares design tokens (CSS custom properties, a Tailwind theme, a `.diagram-design` marker), map these nine variables onto them in the template's `:root` block. Otherwise keep the template defaults. The figures themselves never change.

**Focal rule.** `--accent` goes on the one or two elements the reader must notice: the headline message, the state that matters, the aggregate root. A figure with four accent elements has not decided what is focal.

## The 4px grid

Every coordinate, size, gap, and font size is divisible by 4. Stroke widths (0.8, 1, 1.2) and opacities are exempt. A coordinate ending in 1, 2, 3, 5, 6, 7 or 9 is wrong.

| What | Values |
|---|---|
| Node width x height | 160 x 56 default; 120, 200, 240 wide when text needs it |
| Gap between nodes | 40 horizontal, 48 vertical, minimum 24 |
| Font size | 12 node name, 8 sublabel and arrow label |
| Corner radius | 6 node, 8 elbow, 2 badge |

## Draw order

Background, zones, arrows, nodes, labels. Arrows go before nodes so the node fill hides the arrow tail, and every node starts with an opaque `--paper` mask so nothing bleeds through.

## Skeleton

```svg
<svg viewBox="0 0 960 480" xmlns="http://www.w3.org/2000/svg"
     role="img" aria-labelledby="fig-birdseye-title fig-birdseye-desc">
  <title id="fig-birdseye-title">Order flow from checkout to fulfilment</title>
  <desc id="fig-birdseye-desc">Checkout hands an OrderDraft to the orders module, which persists it and emits OrderCreated to fulfilment.</desc>
  <defs>
    <marker id="arrow" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="var(--muted)"/></marker>
    <marker id="arrow-accent" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="var(--accent)"/></marker>
    <marker id="arrow-link" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="var(--link)"/></marker>
    <marker id="arrow-open" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
      <polyline points="0 0, 8 3, 0 6" fill="none" stroke="var(--muted)" stroke-width="1.2"/></marker>
  </defs>
  <rect width="100%" height="100%" fill="var(--paper)"/>
  <!-- zones, then arrows, then nodes -->
</svg>
```

Accessibility contract, checked by `scripts/self_check.py`: `role="img"`, `aria-labelledby` naming title then desc, `<title>` as the first child, both filled, IDs prefixed with the figure's slug (`fig-<slug>-title`), never bare `title`/`desc`. The `<desc>` says what the figure shows in content terms, never in shapes.

Marker IDs are shared across the page, so define them once in the first `<svg>` and reuse `url(#arrow)` in every later figure. Width is `viewBox` 960; height is the content plus 48 when a legend is needed.

## Node

```svg
<rect x="X" y="Y" width="160" height="56" rx="6" fill="var(--paper)"/>
<rect x="X" y="Y" width="160" height="56" rx="6" fill="FILL" stroke="STROKE" stroke-width="1"/>
<rect x="X+8" y="Y+8" width="32" height="12" rx="2" fill="none" stroke="STROKE" stroke-opacity="0.4" stroke-width="0.8"/>
<text x="X+24" y="Y+17" font-size="8" font-family="var(--font-mono)" fill="STROKE" fill-opacity="0.8"
      text-anchor="middle" letter-spacing="0.08em">MOD</text>
<text x="CX" y="CY+2" font-size="12" font-weight="600" font-family="var(--font-sans)" fill="var(--ink)"
      text-anchor="middle">orders.service</text>
<text x="CX" y="CY+18" font-size="8" font-family="var(--font-mono)" fill="var(--muted)"
      text-anchor="middle">src/orders/service.ts</text>
```

The name line is the real symbol. The sublabel is its path, port, or type. The tag (`MOD`, `FN`, `SYS`, `DB`, `NEW`) is optional and at most four characters.

| Node kind | FILL | STROKE |
|---|---|---|
| Module, function, step | `var(--paper)` | `var(--ink)` |
| Store, table, queue | `var(--ink)` with `fill-opacity="0.05"` | `var(--muted)` |
| External system | `var(--ink)` with `fill-opacity="0.03"` | `var(--ink)` with `stroke-opacity="0.3"` |
| Focal (1 or 2 per figure) | `var(--accent-tint)` | `var(--accent)` |
| New (the feature adds it) | as its kind | `var(--new)`, `stroke-width="2"`, `stroke-dasharray="5 3"` |

A store gets a cylinder feel from a second `rx="6"` rect 8px tall along its top edge. A decision is a diamond: `<polygon points="CX,Y CX+56,CY CX,Y+56 CX-56,CY"/>`. Start and end of a flow are a filled dot `r="6"` and a ringed dot (`r="8"` outline over `r="5"` filled).

## Arrows

| Arrow | Attributes |
|---|---|
| Call, data flow | `stroke="var(--muted)" stroke-width="1.2" marker-end="url(#arrow)"` |
| Crosses a boundary (HTTP, queue, another process) | `stroke="var(--link)"` and `marker-end="url(#arrow-link)"` |
| Return, optional, failure path | add `stroke-dasharray="5 4"` |
| Async, fire-and-forget | dashed with `marker-end="url(#arrow-open)"` |
| Headline (1 or 2 per figure) | `stroke="var(--accent)"` and `marker-end="url(#arrow-accent)"` |

Endpoints that share an x or y use a straight `<line>`. Anything else is an orthogonal elbow with `r=8` corners. A diagonal is a hard fail.

```svg
<!-- right then down, from (x1,y1) to (x2,y2), mid = (x1+x2)/2 -->
<path d="M x1,y1 H mid-8 Q mid,y1 mid,y1+8 V y2-8 Q mid,y2 mid+8,y2 H x2"
      fill="none" stroke="var(--muted)" stroke-width="1.2" marker-end="url(#arrow)"/>
<!-- mainly vertical: leave the source's bottom edge, enter the target's top edge, one bend -->
<path d="M x1,y1 V y2-8 Q x1,y2 x1+8,y2 H x2"
      fill="none" stroke="var(--muted)" stroke-width="1.2" marker-end="url(#arrow)"/>
```

Four rules that keep arrows traceable:

1. Two arrows never share a segment. Offset parallel runs by 12px or more.
2. Several arrows on one edge of a box each get their own attach point, spread `L*k/(N+1)` along the edge, at least 12px apart.
3. An arrow never passes behind a box that is not its endpoint. Reroute around it.
4. When two arrows must cross, the less important one hops: `H cx-8 a 8,8 0 0,1 16,0 H x2` on a horizontal run, `a 8,8 0 0,0 0,16` on a vertical one.

## Arrow labels

Every arrow carries what crosses it, on an opaque mask with a visible 6 to 10px gap to the stroke.

```svg
<rect x="MX-40" y="AY-20" width="80" height="12" rx="2" fill="var(--paper)"/>
<text x="MX" y="AY-11" font-size="8" font-family="var(--font-mono)" fill="var(--soft)"
      text-anchor="middle">OrderCreated</text>
```

Centred above a horizontal run, beside a vertical one. The label sits on open canvas, never where a node painted later will cover it. Decision ids ride the label: `D3 retry via queue`.

## Zones

Ownership groups go behind everything, one level deep.

```svg
<rect x="X" y="Y" width="W" height="H" rx="8" fill="var(--ink)" fill-opacity="0.02"
      stroke="var(--rule)" stroke-width="1"/>
<text x="X+12" y="Y+16" font-size="8" font-family="var(--font-mono)" fill="var(--soft)"
      letter-spacing="0.12em">DOMAIN LAYER</text>
```

## Legend

Only when the figure uses a treatment the reader cannot infer (the `new` dash, the `link` color, the open arrowhead). A horizontal strip below the drawing, never inside it: a `--rule` hairline, then items 160px apart, each a 24px sample of the treatment and an 8px mono caption.

## Check before moving on

- The figure answers its `Figure:` sentence and nothing more. Any node or arrow that could go without loss goes.
- Within the type's budget in [`../diagrams.md`](../diagrams.md).
- Accent on at most two elements. Every label is a real symbol. Every arrow labelled.
- No diagonal, no overlapping strokes, no label on a stroke, everything on the 4px grid.
- `python scripts/self_check.py docs/blueprints/<slug>/BLUEPRINT.html` prints `OK`.
