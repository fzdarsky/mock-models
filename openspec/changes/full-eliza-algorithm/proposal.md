## Why

The current `ElizaMode` implements a simplified ELIZA with 12 flat regex patterns, basic pronoun reflection, and cycling fallbacks. It lacks the key mechanisms that made Weizenbaum's original convincing: keyword priority ranking, two-level decomposition/reassembly rules, synonym classes, memory of earlier topics, and the full DOCTOR script (~80 keywords). Upgrading to the full algorithm makes `mocklm-eliza` a faithful reimplementation suitable for testing conversation flows where response variety and context-awareness matter.

## What Changes

- Replace flat pattern list with a structured keyword/decomposition/reassembly rule engine supporting priority ranking
- Add pre-substitution (input normalization) and post-substitution (pronoun reflection on captured groups only) passes
- Add synonym class expansion in decomposition patterns
- Add keyword delegation (`goto` / `=` rules)
- Implement memory mechanism using conversation history from the messages list (clients already send prior turns as context)
- Port the full DOCTOR script (~80 keywords, ~200 decomposition rules) from the reference elizabot.js implementation
- Add unit tests covering all new engine features before implementing them (TDD approach)

## Capabilities

### New Capabilities

- `eliza-engine`: Core ELIZA algorithm engine — keyword priority, decomposition/reassembly, pre/post substitution, synonym expansion, goto delegation, and memory
- `eliza-script`: Full DOCTOR script data — keywords, decomposition rules, reassembly templates, synonyms, pre/post substitution tables, initial/final phrases

### Modified Capabilities

## Impact

- `mocklm/src/mocklm/modes/eliza.py` — rewrite of the mode implementation
- `mocklm/tests/test_modes.py` — new/updated Eliza tests
- No API changes — `ElizaMode` still implements `Mode.generate(messages)` with the same signature
- No new dependencies
