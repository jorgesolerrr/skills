# Mermaid syntax for the five constructs

Condensed from [Agents365-ai/mermaid-skill](https://github.com/Agents365-ai/mermaid-skill) (MIT) to the types [`diagrams.md`](diagrams.md) uses. Read the section for the type you are drawing.

## Flowchart: bird's-eye, module map, change map, blast radius

```mermaid
flowchart LR
  Client --> Gateway["API gateway"]
  Gateway --> Orders
  Orders --> OrdersDb[(orders)]

  subgraph "Domain layer"
    Orders
  end
```

| Direction | |
|---|---|
| `LR` | left to right: flows |
| `TB` | top to bottom: dependencies, callers above callees |

| Node | Syntax | Use for |
|---|---|---|
| Rectangle | `[text]` | module, function |
| Rounded | `(text)` | process step |
| Diamond | `{text}` | decision |
| Cylinder | `[(text)]` | database, store |
| Subroutine | `[[text]]` | external system |
| Circle | `((text))` | start, end |
| Flag | `>text]` | async event |

| Arrow | Syntax | Use for |
|---|---|---|
| Solid | `-->` | call, data |
| Dashed | `-.->` | optional, async, failure |
| Thick | `==>` | the main path |
| X end | `--x` | termination |
| Line | `---` | relation without direction |

Labels: `A -- "OrderCreated" --> B` or `A -->|"D3: retry"| B`. Fan-out: `A & B --> C`, `C --> D & E`. Node ids are bare words; put the display text in brackets and quote it when it holds `:`, `(`, `[`, `|`, `/`.

Styling: `classDef new stroke:#2e7d32,stroke-width:2px` then `class Foo,Bar new`.

## Sequence: ground-level flows, before-and-after

```mermaid
sequenceDiagram
  participant C as Checkout
  participant Q as OrderQueue (new)
  actor U as User

  C->>+Q: enqueue(order: Order)
  Q-->>-C: Receipt
  Q-xC: enqueue failed
```

Declare `participant`s (box) and `actor`s (stick figure) in the order they act; the alias after `as` is the display text.

| Arrow | Use for |
|---|---|
| `->>` | call |
| `-->>` | return |
| `-x` | failure, fire and forget |
| `-)` | async message |

`+` after the arrow activates the target, `-` deactivates: `C->>+S: req` then `S-->>-C: res`. Or `activate S` / `deactivate S` as lines.

Fragments, one level deep at most:

```mermaid
sequenceDiagram
  loop every 5 s
    C->>S: heartbeat
  end
  alt success
    S-->>C: 200
  else failure
    S-->>C: 500
  end
  opt cached
    C->>S: skip
  end
  par fan-out
    A->>B: do A
  and
    A->>C: do B
  end
```

Notes: `Note right of S: text`, `Note over A,B: text`.

## Class: data shapes, data types changed

```mermaid
classDiagram
  class Order {
    +id: str
    +lines: list[Line]
    -legacy_id: str removed
    +total() Money
  }
  class Line {
    +sku: str
    +qty: int
  }
  Order "1" *-- "*" Line : owns
```

Fields are `<visibility><name>: <Type>`; a member with `()` renders as a method. Text after the type renders as-is, so `+retries: int added` works as a mark. Visibility: `+` public, `-` private, `#` protected, `~` package.

| Relation | Meaning |
|---|---|
| `<\|--` | extends |
| `*--` | owns (composition) |
| `o--` | has (aggregation) |
| `-->` | uses |
| `..>` | depends on |
| `..\|>` | implements |

Cardinality in quotes on either side: `Order "1" --> "1..*" Line`. Values: `1`, `0..1`, `*`, `1..*`, `n..m`. Styling as in flowchart: `classDef` then `class Order changed`.

## ER: schema changes

```mermaid
erDiagram
  USER ||--o{ ORDER : places
  ORDER ||--|{ ORDER_ITEM : contains

  USER {
    int id PK
    string email UK
  }
  ORDER {
    int id PK
    int user_id FK
    string status
  }
```

| Left | Right | Meaning |
|---|---|---|
| `\|\|` | `\|\|` | one to one |
| `\|\|` | `o{` | one to zero or many |
| `\|\|` | `\|{` | one to one or many |
| `o\|` | `o{` | zero or one to zero or many |

Attribute line: `<type> <name> [PK|FK|UK] ["comment"]`.

## State: lifecycles

```mermaid
stateDiagram-v2
  [*] --> Pending
  Pending --> Confirmed : payment_received
  Pending --> Cancelled : timeout
  Confirmed --> Shipped : packed
  Shipped --> [*]
  Cancelled --> [*]

  state Confirmed {
    [*] --> Reserved
    Reserved --> Packed : pick
  }
```

`[*]` is start and end. `A --> B : guard` puts the guard on the transition. `state Name { … }` nests, one level at most.
