## Context

The `ElizaMode` in `mocklm/src/mocklm/modes/eliza.py` currently implements a simplified ELIZA with a flat list of 12 regex patterns, each mapped directly to a list of response strings. It uses a single `_reflect()` function on captured groups and falls back to generic responses when no pattern matches. The `Mode` base class contract is `generate(messages: list[Message]) -> str`, where `messages` contains the full conversation history (all prior user/assistant turns).

Weizenbaum's original ELIZA (1966) uses a more structured algorithm: keywords with priority ranking, multi-level decomposition/reassembly rules, synonym expansion, pre/post substitution, goto delegation, and a memory stack. The reference JS implementation [elizabot.js](https://www.masswerk.at/elizabot/) faithfully ports the DOCTOR script and is the primary source for the rule data.

## Goals / Non-Goals

**Goals:**

- Implement the full ELIZA algorithm as described in Weizenbaum's 1966 paper
- Port the complete DOCTOR script (~80 keywords) from elizabot.js
- Leverage conversation history in `messages` for the memory mechanism (no internal mutable state needed for memory)
- Maintain the `Mode.generate(messages)` interface — drop-in replacement
- TDD: write tests before implementing each engine feature

**Non-Goals:**

- Interactive "teaching mode" for editing the script at runtime
- Loading scripts from external files (the DOCTOR script is embedded in Python)
- Faithfully reproducing MAD-SLIP implementation details — we replicate the algorithm, not the language
- Supporting multiple simultaneous scripts

## Decisions

### 1. Script data as a Python module

**Decision:** Store the DOCTOR script (keywords, synonyms, pre/post substitutions) in a separate `eliza_script.py` module as typed dataclasses/dicts, not in `eliza.py`.

**Rationale:** The script is ~200 rules of pure data. Mixing it into the engine obscures the algorithm. A separate module mirrors Weizenbaum's original separation of engine from script. Typed dataclasses provide IDE support and validation.

**Alternative considered:** JSON/YAML file loaded at import time — rejected because it adds file I/O, loses type checking, and the data is static.

### 2. Memory via conversation history, not internal state

**Decision:** Implement memory by scanning the `messages` list for earlier user inputs and generating a response from a randomly selected earlier turn, rather than maintaining an internal memory deque across calls.

**Rationale:** The OpenAI chat completions API convention is that clients send the full conversation history on every request. The `messages` list already contains prior turns. This makes `ElizaMode` stateless for memory (only response-rotation indices remain as state), which is simpler and correct for HTTP-based usage where each request may hit a different server instance.

**How it works:** When a decomposition rule is marked as memory-producing (`$` prefix in the original), the engine processes it but instead of returning the response, it stores nothing — the response is discarded. On a no-match input, the engine picks an earlier user message from `messages`, applies a memory-tagged decomposition to it, and returns that response. This simulates "remembering" an earlier topic.

**Alternative considered:** Internal `deque` like the original — rejected because it requires sticky sessions and breaks in stateless HTTP deployments.

### 3. Rule data structures

**Decision:** Use three dataclasses:

```python
@dataclass
class Reassembly:
    template: str
    is_memory: bool = False

@dataclass
class Decomposition:
    pattern: str              # wildcard pattern with * and @synonym
    reassemblies: list[Reassembly]

@dataclass
class Keyword:
    word: str
    rank: int
    decompositions: list[Decomposition]
```

**Rationale:** Maps directly to the original's three-level structure. `is_memory` on `Reassembly` marks the `$`-prefixed rules. Patterns use `*` wildcards and `@synonym` references, compiled to regex at init time.

### 4. Response rotation via instance state

**Decision:** Keep `_keyword_index` and `_fallback_index` as instance state (as today), tracking which reassembly to use next for each decomposition.

**Rationale:** Response cycling is how ELIZA avoids repeating itself. This state is lightweight and acceptable to lose on restart. It's also not derivable from conversation history (unlike memory).

### 5. Processing pipeline order

**Decision:** Follow the original algorithm's pipeline:

1. Strip trailing punctuation
2. Apply pre-substitutions (normalize contractions, etc.)
3. Extract keywords, sort by priority (highest first)
4. For the top keyword, try decompositions in order
5. On match: if decomposition is memory-flagged, skip and try next keyword; otherwise apply post-substitution to captured groups and fill reassembly template
6. On no match for any keyword: try memory (pick an earlier user turn, apply memory-tagged rules)
7. Final fallback: use `xnone` default responses

**Rationale:** This is the documented algorithm. Deviating would break script compatibility.

## Risks / Trade-offs

- **Script transcription errors** → Mitigated by unit tests per keyword category and by cross-referencing elizabot.js data directly.
- **Stateless memory is less faithful** → The original accumulates a FIFO of "saved" responses. Our approach re-derives from history, which may produce different memory responses. Acceptable for a mock model; the behavior is similar enough.
- **Response rotation state is lost on restart** → Acceptable for a mock model. Could be seeded from `len(messages)` for rough continuity if needed later.
- **Large script module** → ~400 lines of data. Acceptable; it's static and well-structured.
