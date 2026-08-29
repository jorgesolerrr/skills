# Class diagram: the data-shapes figure

Answers: what fields does this type carry, and what does it hold or point to?

Every type the feature adds or changes is a box here. Fields are drawn, never pasted from the code.

## Layout

- Each type is one box `rx="6"`, 200 wide, height by content. Hairlines split it into compartments: name, then fields, then operations. A compartment with nothing in it is omitted.
  - **Name**: 12px sans, weight 600, centred. An interface carries an 8px mono `<<interface>>` line above the name. Abstract names are italic.
  - **Fields**: one per line, 8px mono, left-aligned with 12px padding, 16px line height: `status: OrderStatus`, `items: LineItem[]`.
  - **Operations**: only the ones a decision depends on: `apply(event: OrderEvent): Order`.
- Boxes 48px apart, laid out so relations run straight or with one elbow. Owners above or left of what they own.
- New types take the `new` stroke and a `NEW` tag. Changed types show only the fields that changed or that a decision cites, plus one `...` line.
- Accent on the aggregate root or the type the feature is about.

## Relations

Define the markers once in `<defs>` of the first figure that needs them.

| Relation | Line | End at the owner or parent |
|---|---|---|
| Composition (part dies with the whole) | solid | filled diamond, `--ink` |
| Aggregation (part outlives the whole) | solid | hollow diamond, `--paper` fill, `--ink` stroke |
| Reference, association | solid | `#arrow`, multiplicity at both ends |
| Extends | solid | hollow triangle |
| Implements | dashed `5 4` | hollow triangle |
| Uses | dashed `4 3` | `#arrow` |

```svg
<marker id="diamond-filled" markerWidth="12" markerHeight="8" refX="0" refY="4" orient="auto">
  <polygon points="0 4, 6 0, 12 4, 6 8" fill="var(--ink)"/></marker>
<marker id="diamond-hollow" markerWidth="12" markerHeight="8" refX="0" refY="4" orient="auto">
  <polygon points="0 4, 6 0, 12 4, 6 8" fill="var(--paper)" stroke="var(--ink)" stroke-width="1"/></marker>
<marker id="triangle-hollow" markerWidth="10" markerHeight="10" refX="10" refY="5" orient="auto">
  <polygon points="0 0, 10 5, 0 10" fill="var(--paper)" stroke="var(--ink)" stroke-width="1"/></marker>
```

Multiplicities (`1`, `0..*`) are 8px mono on a mask, 12px off the box edge.

## Budget

At most 8 classes, 5 fields per compartment (then `...`), 2 accent elements. Past that, split by module.
