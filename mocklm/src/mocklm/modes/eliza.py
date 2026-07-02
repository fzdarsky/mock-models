import re

from mocklm.models import Message, extract_text
from mocklm.modes.base import Mode
from mocklm.modes.eliza_script import (
    KEYWORDS,
    POST_SUBSTITUTIONS,
    POST_TRANSFORMS,
    PRE_SUBSTITUTIONS,
    SYNONYMS,
    Decomposition,
    Keyword,
)


def _apply_pre_substitutions(text: str) -> str:
    words = text.split()
    result = []
    for word in words:
        lower = word.lower()
        replaced = False
        for src, dst in PRE_SUBSTITUTIONS:
            if lower == src:
                result.append(dst)
                replaced = True
                break
        if not replaced:
            result.append(word)
    return " ".join(result)


def _apply_post_substitutions(text: str) -> str:
    words = text.split()
    result = []
    for word in words:
        lower = word.lower()
        replaced = False
        for src, dst in POST_SUBSTITUTIONS:
            if lower == src:
                result.append(dst)
                replaced = True
                break
        if not replaced:
            result.append(word)
    return " ".join(result)


def _compile_pattern(pattern: str) -> re.Pattern[str]:
    parts = pattern.strip().split()
    is_wild = []
    regex_parts = []
    for part in parts:
        if part == "*":
            regex_parts.append("(.*)")
            is_wild.append(True)
        elif part.startswith("@"):
            synon_name = part[1:]
            words = SYNONYMS.get(synon_name, [synon_name])
            regex_parts.append("(" + "|".join(re.escape(w) for w in words) + ")")
            is_wild.append(False)
        else:
            regex_parts.append(re.escape(part))
            is_wild.append(False)
    joined = regex_parts[0] if regex_parts else ""
    for i in range(1, len(regex_parts)):
        sep = r"\s*" if is_wild[i] or is_wild[i - 1] else r"\s+"
        joined += sep + regex_parts[i]
    regex = r"^\s*" + joined + r"\s*$"
    return re.compile(regex, re.IGNORECASE)


def _apply_post_transforms(text: str) -> str:
    for pattern, replacement in POST_TRANSFORMS:
        text = re.sub(pattern, replacement, text)
    return text


class ElizaMode(Mode):
    def __init__(self) -> None:
        self._decomp_index: dict[int, int] = {}
        self._keyword_map: dict[str, Keyword] = {}
        self._compiled: dict[int, list[tuple[Decomposition, re.Pattern[str], bool]]] = {}

        for kw in KEYWORDS:
            self._keyword_map[kw.word] = kw
            compiled_decomps = []
            for decomp in kw.decompositions:
                pat = decomp.pattern
                is_memory_rule = pat.startswith("$ ")
                if is_memory_rule:
                    pat = pat[2:]
                compiled_decomps.append((decomp, _compile_pattern(pat), is_memory_rule))
            self._compiled[id(kw)] = compiled_decomps

    def generate(self, messages: list[Message]) -> str:
        text = extract_text(messages).strip()
        text = re.sub(r"[.!]+$", "", text)

        if not text:
            return self._default_response()

        text = _apply_pre_substitutions(text)
        keywords = self._extract_keywords(text)

        for kw in keywords:
            response = self._try_keyword(kw, text, skip_memory=True)
            if response:
                return _apply_post_transforms(response)

        memory_response = self._try_memory(messages)
        if memory_response:
            return _apply_post_transforms(memory_response)

        return self._default_response()

    def _extract_keywords(self, text: str) -> list[Keyword]:
        words = set(text.lower().split())
        found = []
        for kw in KEYWORDS:
            if kw.word == "xnone":
                continue
            if kw.word in words:
                found.append(kw)
        found.sort(key=lambda k: k.rank, reverse=True)
        return found

    def _try_keyword(self, kw: Keyword, text: str, skip_memory: bool = False, depth: int = 0) -> str | None:
        if depth > 10:
            return None
        compiled_decomps = self._compiled.get(id(kw), [])
        for decomp, pattern, is_memory_rule in compiled_decomps:
            if skip_memory and is_memory_rule:
                continue
            match = pattern.match(text)
            if match:
                return self._apply_reassembly(decomp, match, text, depth)
        return None

    def _apply_reassembly(self, decomp: Decomposition, match: re.Match[str], text: str, depth: int = 0) -> str | None:
        key = id(decomp)
        idx = self._decomp_index.get(key, 0)
        reassemblies = decomp.reassemblies
        if not reassemblies:
            return None

        reassembly = reassemblies[idx % len(reassemblies)]
        self._decomp_index[key] = idx + 1

        template = reassembly.template

        if template.startswith("goto "):
            target_word = template[5:]
            target_kw = self._keyword_map.get(target_word)
            if target_kw:
                return self._try_keyword(target_kw, text, depth=depth + 1)
            return None

        groups = match.groups()
        result = template
        for i, group in enumerate(groups, 1):
            placeholder = f"({i})"
            if placeholder in result and group is not None:
                reflected = _apply_post_substitutions(group.strip())
                result = result.replace(placeholder, reflected)

        return result

    def _try_memory(self, messages: list[Message]) -> str | None:
        user_messages = []
        for msg in messages:
            if msg.role == "user" and msg.content and isinstance(msg.content, str):
                user_messages.append(msg.content)

        if len(user_messages) < 2:
            return None

        for earlier_text in reversed(user_messages[:-1]):
            earlier_text = re.sub(r"[.!]+$", "", earlier_text.strip())
            earlier_text = _apply_pre_substitutions(earlier_text)

            for kw in KEYWORDS:
                compiled_decomps = self._compiled.get(id(kw), [])
                for decomp, pattern, is_memory_rule in compiled_decomps:
                    if not is_memory_rule:
                        continue
                    match = pattern.match(earlier_text)
                    if match:
                        return self._apply_reassembly(decomp, match, earlier_text)

        return None

    def _default_response(self) -> str:
        xnone = self._keyword_map.get("xnone")
        if xnone and xnone.decompositions:
            decomp = xnone.decompositions[0]
            key = id(decomp)
            idx = self._decomp_index.get(key, 0)
            reassemblies = decomp.reassemblies
            if reassemblies:
                response = reassemblies[idx % len(reassemblies)].template
                self._decomp_index[key] = idx + 1
                return response
        return "Please go on."
