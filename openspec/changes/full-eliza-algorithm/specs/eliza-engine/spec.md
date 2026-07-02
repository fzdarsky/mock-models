## ADDED Requirements

### Requirement: Keyword priority ranking

The engine SHALL extract all recognized keywords from the user input and process them in descending priority order. If a keyword produces a response, that response SHALL be returned immediately without processing lower-priority keywords.

#### Scenario: Multiple keywords with different priorities

- **WHEN** user input contains keywords "dream" (rank 3) and "my" (rank 2)
- **THEN** the engine processes "dream" first because it has higher rank

#### Scenario: Single keyword

- **WHEN** user input contains only one keyword
- **THEN** that keyword's decompositions are tried regardless of rank

### Requirement: Decomposition pattern matching

Each keyword SHALL have one or more decomposition patterns tried in definition order. Decomposition patterns SHALL use `*` as a wildcard matching zero or more words. The first matching decomposition SHALL be selected.

#### Scenario: Wildcard matching

- **WHEN** keyword "i" has decomposition pattern `* i am *` and input is "sometimes i am sad"
- **THEN** the decomposition matches with captured groups ["sometimes", "sad"]

#### Scenario: No matching decomposition

- **WHEN** no decomposition pattern matches the input for a keyword
- **THEN** the engine moves to the next keyword by priority

### Requirement: Reassembly template expansion

Each decomposition SHALL have one or more reassembly templates. The engine SHALL cycle through reassemblies on successive matches (round-robin). Reassembly templates SHALL use `(n)` notation to reference captured groups from the decomposition, where n is 1-based.

#### Scenario: Group insertion

- **WHEN** reassembly template is "Why do you need (2)?" and captured group 2 is "help"
- **THEN** the response is "Why do you need help?"

#### Scenario: Cycling through reassemblies

- **WHEN** a decomposition has 3 reassembly templates and is matched 4 times
- **THEN** the 4th match uses the 1st reassembly template (wraps around)

### Requirement: Pre-substitution

The engine SHALL apply pre-substitution replacements to user input before keyword extraction. Pre-substitutions normalize contractions and alternate phrasings to canonical forms the decomposition patterns expect.

#### Scenario: Contraction normalization

- **WHEN** user input contains "don't"
- **THEN** it is replaced with "dont" before pattern matching (per the original DOCTOR script convention)

### Requirement: Post-substitution on captured groups

The engine SHALL apply post-substitution (pronoun/perspective reflection) to captured groups before inserting them into reassembly templates. Post-substitution SHALL NOT be applied to the template text itself.

#### Scenario: Pronoun reflection in captured group

- **WHEN** captured group is "my mother" and post-substitutions include "my" → "your"
- **THEN** the group becomes "your mother" before insertion into the reassembly template

#### Scenario: Template text unchanged

- **WHEN** reassembly template is "Why do you say (1)?" with captured group "I am tired"
- **THEN** "you" in the template is not affected by post-substitution; only the group "I am tired" becomes "you are tired"

### Requirement: Synonym expansion in decompositions

Decomposition patterns SHALL support `@synonymClass` notation that matches any word in the named synonym group. The synonym class reference SHALL match any single word from that group.

#### Scenario: Belief synonym class

- **WHEN** a decomposition pattern contains `@belief` and the synonym group "belief" includes ["believe", "feel", "think", "wish"]
- **THEN** the pattern matches input containing any of those four words

### Requirement: Keyword delegation (goto)

A reassembly rule SHALL support delegation to another keyword via a `goto <keyword>` directive. When encountered, the engine SHALL process the target keyword's decompositions as if it were the matched keyword.

#### Scenario: Goto delegation

- **WHEN** keyword "everyone" has a reassembly "goto everybody"
- **THEN** the engine processes keyword "everybody"'s decompositions against the current input

#### Scenario: Missing goto target

- **WHEN** a goto references a keyword that does not exist in the script
- **THEN** the engine falls through to the next keyword or fallback

### Requirement: Memory mechanism via conversation history

When no keyword match produces a response, the engine SHALL attempt to use earlier user messages from the conversation history as a memory source. The engine SHALL apply memory-tagged decomposition rules to an earlier user message and return that response.

#### Scenario: Memory fallback

- **WHEN** current input matches no keyword and conversation history contains a previous user message "my father was strict"
- **THEN** the engine MAY apply a memory-tagged decomposition to "my father was strict" and return a response about it

#### Scenario: No conversation history

- **WHEN** current input matches no keyword and there are no previous user messages
- **THEN** the engine uses the default fallback responses

### Requirement: Default fallback responses

The engine SHALL maintain a set of default responses (the `xnone` keyword) used when no keyword match and no memory response is available. Default responses SHALL cycle on successive uses.

#### Scenario: No match anywhere

- **WHEN** input contains no recognized keywords, no memory is available
- **THEN** a response from the default set is returned (e.g., "Please go on.")

### Requirement: Input normalization

The engine SHALL strip trailing punctuation (`.`, `!`) from user input before processing. The engine SHALL preserve `?` for question-pattern matching.

#### Scenario: Trailing period stripped

- **WHEN** user input is "I need help."
- **THEN** the engine processes "I need help" (without the period)

#### Scenario: Question mark preserved

- **WHEN** user input is "Are you a computer?"
- **THEN** the `?` is available for question-pattern matching

### Requirement: Mode interface compatibility

`ElizaMode` SHALL implement the `Mode.generate(messages: list[Message]) -> str` interface. It SHALL be a drop-in replacement for the current implementation.

#### Scenario: Drop-in replacement

- **WHEN** `ElizaMode().generate([Message(role="user", content="Hello")])` is called
- **THEN** a non-empty string response is returned
