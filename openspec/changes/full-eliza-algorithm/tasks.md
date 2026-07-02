## 1. Data structures and script module

- [x] 1.1 Create `eliza_script.py` with dataclasses: `Reassembly`, `Decomposition`, `Keyword`
- [x] 1.2 Add pre-substitution table (contractions and normalization)
- [x] 1.3 Add post-substitution table (pronoun/perspective reflection pairs)
- [x] 1.4 Add synonym groups (belief, family, desire, sad, happy, etc.)
- [x] 1.5 Add quit phrases, initial greetings, and farewell phrases
- [x] 1.6 Add default responses (`xnone` keyword)
- [x] 1.7 Port full DOCTOR keyword set from elizabot.js (~80 keywords with decompositions and reassemblies, including memory-tagged rules)

## 2. Tests for engine features (TDD — write before implementation)

- [x] 2.1 Test keyword priority ranking: highest-rank keyword fires first
- [x] 2.2 Test decomposition wildcard matching: `*` captures zero or more words
- [x] 2.3 Test reassembly template expansion: `(n)` group references replaced correctly
- [x] 2.4 Test reassembly cycling: round-robin through responses on repeated matches
- [x] 2.5 Test pre-substitution: contractions normalized before matching
- [x] 2.6 Test post-substitution: pronoun reflection applied to captured groups only
- [x] 2.7 Test synonym expansion: `@belief` matches "believe", "feel", "think", etc.
- [x] 2.8 Test goto delegation: keyword delegates to another keyword's rules
- [x] 2.9 Test memory via conversation history: earlier user message used when no keyword matches
- [x] 2.10 Test default fallback: `xnone` responses used when no match and no memory
- [x] 2.11 Test input normalization: trailing `.` and `!` stripped, `?` preserved
- [x] 2.12 Test Mode interface compatibility: `ElizaMode().generate(messages)` returns non-empty string

## 3. Engine implementation

- [x] 3.1 Implement input normalization and pre-substitution pipeline
- [x] 3.2 Implement keyword extraction and priority sorting from input text
- [x] 3.3 Implement decomposition pattern compilation (wildcards `*` and `@synonym` expansion to regex)
- [x] 3.4 Implement reassembly template expansion with `(n)` group insertion and post-substitution
- [x] 3.5 Implement reassembly cycling (per-decomposition round-robin index)
- [x] 3.6 Implement goto/delegation handling with loop guard
- [x] 3.7 Implement memory mechanism: scan earlier user messages from `messages` list, apply memory-tagged decompositions
- [x] 3.8 Implement `ElizaMode.generate()` tying the full pipeline together
- [x] 3.9 Update `__init__.py` mode registration if needed

## 4. Verification

- [x] 4.1 Run all tests and confirm they pass
- [x] 4.2 Manually test with sample conversations (reproduce Weizenbaum's published example exchange)
- [x] 4.3 Remove or update any obsolete tests from the old implementation
