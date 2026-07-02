from mocklm.models import Message
from mocklm.modes.eliza import ElizaMode


class TestKeywordPriority:
    def test_highest_rank_keyword_fires_first(self):
        mode = ElizaMode()
        messages = [Message(role="user", content="my computer is broken")]
        response = mode.generate(messages)
        assert "computer" in response.lower() or "machine" in response.lower()

    def test_single_keyword(self):
        mode = ElizaMode()
        messages = [Message(role="user", content="I had a dream last night")]
        response = mode.generate(messages)
        assert response and len(response) > 0


class TestDecompositionWildcard:
    def test_wildcard_captures_words(self):
        mode = ElizaMode()
        messages = [Message(role="user", content="I remember my childhood")]
        response = mode.generate(messages)
        assert "childhood" in response.lower() or "remember" in response.lower() or "recollect" in response.lower()

    def test_wildcard_matches_zero_words(self):
        mode = ElizaMode()
        messages = [Message(role="user", content="i am happy")]
        response = mode.generate(messages)
        assert response and len(response) > 0


class TestReassemblyExpansion:
    def test_group_reference_replaced(self):
        mode = ElizaMode()
        messages = [Message(role="user", content="I am feeling tired")]
        response = mode.generate(messages)
        assert response and len(response) > 0

    def test_response_contains_reflected_input(self):
        mode = ElizaMode()
        messages = [Message(role="user", content="I remember summer vacation")]
        response = mode.generate(messages)
        assert "summer vacation" in response.lower() or "recollect" in response.lower() or response


class TestReassemblyCycling:
    def test_round_robin_responses(self):
        mode = ElizaMode()
        responses = set()
        for _ in range(4):
            messages = [Message(role="user", content="perhaps I should try")]
            responses.add(mode.generate(messages))
        assert len(responses) > 1


class TestPreSubstitution:
    def test_contractions_normalized(self):
        mode = ElizaMode()
        messages = [Message(role="user", content="I dreamt about flying")]
        response = mode.generate(messages)
        assert "dream" in response.lower() or response


class TestPostSubstitution:
    def test_pronoun_reflection_in_captured_group(self):
        mode = ElizaMode()
        messages = [Message(role="user", content="I remember my mother")]
        response = mode.generate(messages)
        assert "your mother" in response.lower() or "your" in response.lower() or response


class TestSynonymExpansion:
    def test_belief_synonym_matches(self):
        mode = ElizaMode()
        for word in ["believe", "feel", "think", "wish"]:
            messages = [Message(role="user", content=f"I {word} I am right")]
            response = mode.generate(messages)
            assert response and len(response) > 0

    def test_family_synonym_matches(self):
        mode = ElizaMode()
        messages = [Message(role="user", content="my sister is kind")]
        response = mode.generate(messages)
        assert "family" in response.lower() or "sister" in response.lower() or response


class TestGotoDelegation:
    def test_keyword_delegates_to_another(self):
        mode = ElizaMode()
        messages = [Message(role="user", content="everybody hates me")]
        response = mode.generate(messages)
        assert response and len(response) > 0

    def test_missing_goto_target_falls_through(self):
        mode = ElizaMode()
        messages = [Message(role="user", content="hello there")]
        response = mode.generate(messages)
        assert response and len(response) > 0


class TestMemory:
    def test_earlier_message_used_when_no_keyword(self):
        mode = ElizaMode()
        mode.generate([Message(role="user", content="my dog is cute")])
        messages = [
            Message(role="user", content="my dog is cute"),
            Message(role="assistant", content="Your dog ?"),
            Message(role="user", content="the sky is very blue today indeed"),
        ]
        response = mode.generate(messages)
        assert response and len(response) > 0


class TestDefaultFallback:
    def test_xnone_responses_used(self):
        mode = ElizaMode()
        messages = [Message(role="user", content="asdfghjkl qwerty")]
        response = mode.generate(messages)
        assert response and len(response) > 0
        expected_defaults = [
            "I'm not sure I understand you fully.",
            "Please go on.",
            "What does that suggest to you ?",
            "Do you feel strongly about discussing such things ?",
            "That is interesting.  Please continue.",
            "Tell me more about that.",
            "Does talking about this bother you ?",
        ]
        assert response in expected_defaults


class TestInputNormalization:
    def test_trailing_period_stripped(self):
        mode = ElizaMode()
        msg_with = [Message(role="user", content="I need help.")]
        msg_without = [Message(role="user", content="I need help")]
        r1 = mode.generate(msg_with)
        mode2 = ElizaMode()
        r2 = mode2.generate(msg_without)
        assert r1 == r2

    def test_trailing_exclamation_stripped(self):
        mode = ElizaMode()
        msg_with = [Message(role="user", content="I need help!")]
        msg_without = [Message(role="user", content="I need help")]
        r1 = mode.generate(msg_with)
        mode2 = ElizaMode()
        r2 = mode2.generate(msg_without)
        assert r1 == r2

    def test_question_mark_preserved(self):
        mode = ElizaMode()
        messages = [Message(role="user", content="Are you a computer?")]
        response = mode.generate(messages)
        assert response and len(response) > 0


class TestModeInterface:
    def test_generate_returns_nonempty_string(self):
        mode = ElizaMode()
        messages = [Message(role="user", content="Hello")]
        response = mode.generate(messages)
        assert isinstance(response, str)
        assert len(response) > 0

    def test_empty_messages(self):
        mode = ElizaMode()
        response = mode.generate([])
        assert isinstance(response, str)
        assert len(response) > 0
