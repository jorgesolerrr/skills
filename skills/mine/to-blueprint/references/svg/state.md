# State machine: a ground-level figure for a lifecycle

Answers: what states can this thing be in, and what moves it?

## Layout

- States are rounded rectangles `rx="8"`, 120 x 40, named by the real enum value or status string. Laid out along the dominant direction (left to right for a pipeline, top to bottom for a lifecycle), arranged so no transition crosses another.
- Start is a filled dot `r="6"`. End is a ringed dot. Both sit on the axis of the flow.
- Transitions are elbow arrows labelled `event [guard] / action`, each part only when it exists: `paid`, `timeout [retries < 3] / requeue`. An unlabelled transition is a missing decision.
- A self-loop is a small arc above the state, label above the arc.
- Transitions "from any state" are one annotation in 8px mono at the bottom (`* -> Failed on timeout`), never an arrow from every state.
- Accent on the one state the reader should notice: usually the terminal error state or the success state.

## Budget

At most 8 states. Transitions past twice the state count mean two machines: split by the object that owns each.
