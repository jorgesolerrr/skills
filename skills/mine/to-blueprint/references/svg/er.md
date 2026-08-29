# ER diagram: the data-shapes figure for a schema change

Answers: what tables exist and how do they relate?

Draw one when the feature adds or alters a table. Types in code stay in the class diagram.

## Layout

- Each table is a two-part box `rx="6"`, 200 wide, height by content. Header: `TABLE` tag and the table name in 12px sans. Body: one column per line in 8px mono, 16px line height, `name type`. Primary key first, prefixed `#`. Foreign keys prefixed `->` with the target table.
- Show the columns the feature adds or that a relation depends on, then one `...` line. A new table takes the `new` stroke; a new column on an existing table is its own line in `--new` fill colour.
- Relations are lines box to box, straight when the layout allows. Cardinality at each end in 8px mono, 12px off the edge: `1`, `N`, `0..1`. Optional verb on a mask at the midpoint: `has`, `belongs to`.
- Lay out by cluster so most relations are straight. The aggregate root sits at the left or top and takes the accent.

## Budget

At most 8 tables. A relation for every foreign key only up to that count; past it, cluster and caption.
