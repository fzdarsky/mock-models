## ADDED Requirements

### Requirement: DOCTOR script keyword coverage

The script module SHALL contain the full DOCTOR script keywords as defined in the elizabot.js reference implementation. This includes approximately 80 keywords covering topics such as: personal pronouns, feelings, family, dreams, computers, apologies, memory triggers, and general conversational patterns.

#### Scenario: Core keyword categories present

- **WHEN** the script is loaded
- **THEN** it contains keywords for at least: "i", "you", "my", "we", "mother", "father", "dream", "computer", "sorry", "hello", "yes", "no", "perhaps", "name", "remember", "if", "what", "how", "because", "why", "everyone", "always", "alike", "like"

#### Scenario: Keyword count

- **WHEN** the script is loaded
- **THEN** it contains at least 60 keywords (the original has approximately 80)

### Requirement: Pre-substitution table

The script SHALL provide a pre-substitution table that normalizes user input before keyword matching. This includes expanding contractions and normalizing alternate phrasings.

#### Scenario: Standard contractions

- **WHEN** the pre-substitution table is applied
- **THEN** it maps entries like "don't" → "dont", "can't" → "cant", "won't" → "wont", "i'm" → "im"

### Requirement: Post-substitution table

The script SHALL provide a post-substitution table for pronoun/perspective reflection applied to captured groups. This mirrors the user's perspective back in responses.

#### Scenario: Pronoun reflection pairs

- **WHEN** the post-substitution table is applied to a captured group
- **THEN** it maps "my" → "your", "your" → "my", "me" → "you", "you" → "me", "i" → "you", "am" → "are", "myself" → "yourself", and their reverses

### Requirement: Synonym groups

The script SHALL define synonym groups that allow decomposition patterns to match any word in a semantic class with a single `@class` reference.

#### Scenario: Belief synonyms

- **WHEN** the synonym group "belief" is defined
- **THEN** it includes at least ["believe", "feel", "think", "wish"]

#### Scenario: Family synonyms

- **WHEN** the synonym group "family" is defined
- **THEN** it includes at least ["mother", "mom", "father", "dad", "sister", "brother", "wife", "husband"]

### Requirement: Default responses (xnone)

The script SHALL provide a set of default responses used when no keyword matches. These SHALL be the `xnone` keyword's reassembly templates.

#### Scenario: Default response variety

- **WHEN** the default response set is loaded
- **THEN** it contains at least 5 distinct responses

### Requirement: Initial and final phrases

The script SHALL provide initial greeting phrases and final farewell phrases for conversation lifecycle.

#### Scenario: Initial phrases

- **WHEN** an initial phrase is requested
- **THEN** it returns a greeting such as "How do you do. Please tell me your problem."

#### Scenario: Final phrases

- **WHEN** a final phrase is requested
- **THEN** it returns a farewell such as "Goodbye. Thank you for talking to me."

### Requirement: Quit phrases

The script SHALL define quit phrases that signal the end of a conversation.

#### Scenario: Standard quit phrases

- **WHEN** the quit phrase list is checked
- **THEN** it includes at least ["bye", "goodbye", "quit", "done"]

### Requirement: Memory-tagged decompositions

Certain decomposition rules in the script SHALL be tagged as memory-producing (the `$` prefix convention). These rules indicate that the matched input should be available for recall when a future input has no keyword match.

#### Scenario: Memory tags on personal keywords

- **WHEN** the keyword "my" is loaded
- **THEN** at least one of its decompositions has a memory-tagged reassembly
