import re

from mocklm.models import Message, extract_text
from mocklm.modes.base import Mode

REFLECTIONS = {
    "i am": "you are",
    "i was": "you were",
    "i": "you",
    "i'm": "you are",
    "i'd": "you would",
    "i've": "you have",
    "i'll": "you will",
    "my": "your",
    "me": "you",
    "am": "are",
    "you are": "I am",
    "you were": "I was",
    "you've": "I have",
    "you'll": "I will",
    "your": "my",
    "yours": "mine",
    "you": "me",
    "myself": "yourself",
    "yourself": "myself",
}

KEYWORDS: list[tuple[str, list[str]]] = [
    (
        r"i need (.*)",
        [
            "Why do you need {0}?",
            "Would it really help you to get {0}?",
            "Are you sure you need {0}?",
        ],
    ),
    (
        r"why don'?t you (.*)",
        [
            "Do you really think I don't {0}?",
            "Perhaps eventually I will {0}.",
            "Do you really want me to {0}?",
        ],
    ),
    (
        r"why can'?t i (.*)",
        [
            "Do you think you should be able to {0}?",
            "If you could {0}, what would you do?",
            "What do you think is stopping you from being able to {0}?",
        ],
    ),
    (
        r"i can'?t (.*)",
        [
            "How do you know you can't {0}?",
            "Perhaps you could {0} if you tried.",
            "What would it take for you to {0}?",
        ],
    ),
    (
        r"i am (.*)",
        [
            "How long have you been {0}?",
            "How do you feel about being {0}?",
            "What made you feel {0}?",
        ],
    ),
    (
        r"i'm (.*)",
        [
            "How does being {0} make you feel?",
            "Do you enjoy being {0}?",
            "Why do you tell me you're {0}?",
        ],
    ),
    (
        r"are you (.*)",
        [
            "Why does it matter whether I am {0}?",
            "Would you prefer it if I were not {0}?",
            "Perhaps you believe I am {0}.",
        ],
    ),
    (
        r"i feel (.*)",
        [
            "Tell me more about feeling {0}.",
            "Do you often feel {0}?",
            "When you feel {0}, what do you do?",
        ],
    ),
    (
        r"(.*)\b(mother|mom|father|dad|parent)\b(.*)",
        [
            "Tell me more about your family.",
            "How does that make you feel about your family?",
            "What role did your family play in your life?",
        ],
    ),
    (
        r"(.*)\b(dream|dreams)\b(.*)",
        [
            "What does that dream suggest to you?",
            "Do you dream often?",
            "What persons appear in your dreams?",
        ],
    ),
    (
        r"hello|hi|hey(.*)",
        [
            "Hello! How are you feeling today?",
            "Hi there. What's on your mind?",
            "Hey. Tell me what's been going on.",
        ],
    ),
    (
        r"(.*)\?",
        [
            "Why do you ask that?",
            "What do you think?",
            "Does that question interest you?",
        ],
    ),
]

FALLBACKS = [
    "Tell me more.",
    "How does that make you feel?",
    "Can you elaborate on that?",
    "Why do you say that?",
    "I see. Please go on.",
    "That is interesting. Please continue.",
    "How do you feel when you say that?",
]


def _reflect(text: str) -> str:
    words = text.lower().split()
    result = []
    i = 0
    while i < len(words):
        if i < len(words) - 1:
            bigram = f"{words[i]} {words[i + 1]}"
            if bigram in REFLECTIONS:
                result.append(REFLECTIONS[bigram])
                i += 2
                continue
        result.append(REFLECTIONS.get(words[i], words[i]))
        i += 1
    return " ".join(result)


class ElizaMode(Mode):
    def __init__(self) -> None:
        self._keyword_index: dict[str, int] = {}
        self._fallback_index = 0

    def generate(self, messages: list[Message]) -> str:
        text = extract_text(messages).strip()

        if not text:
            return self._next_fallback()

        for pattern, responses in KEYWORDS:
            match = re.match(pattern, text, re.IGNORECASE)
            if match:
                group = _reflect(match.group(match.lastindex or 1)) if match.lastindex else ""
                idx = self._keyword_index.get(pattern, 0)
                response = responses[idx % len(responses)]
                self._keyword_index[pattern] = idx + 1
                return response.format(group.strip()) if "{0}" in response else response

        return self._next_fallback()

    def _next_fallback(self) -> str:
        response = FALLBACKS[self._fallback_index % len(FALLBACKS)]
        self._fallback_index += 1
        return response
