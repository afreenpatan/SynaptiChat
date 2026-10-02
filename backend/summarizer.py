import re
from collections import Counter


# ============================================================
# STOP WORDS
# ============================================================

STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "if", "then",
    "is", "are", "was", "were", "be", "been", "being",
    "to", "of", "in", "on", "at", "for", "from", "with",
    "by", "as", "it", "this", "that", "these", "those",
    "we", "i", "you", "he", "she", "they", "me", "my",
    "our", "your", "their", "will", "would", "can", "could",
    "should", "shall", "do", "does", "did", "have", "has",
    "had", "am", "not", "so", "very", "just", "please",
    "let", "us"
}


# ============================================================
# ACTION WORDS
# ============================================================

ACTION_VERBS = {
    "complete",
    "finish",
    "prepare",
    "send",
    "share",
    "test",
    "update",
    "review",
    "create",
    "build",
    "develop",
    "design",
    "submit",
    "check",
    "fix",
    "write",
    "collect",
    "present",
    "upload",
    "download",
    "implement",
    "deploy",
    "analyze",
    "discuss",
    "finalize",
    "report",
    "deliver",
    "work",
    "prepare",
    "make",
    "start",
    "continue"
}


# ============================================================
# DEADLINE WORDS
# ============================================================

DEADLINE_PATTERNS = [
    r"\btoday\b",
    r"\btomorrow\b",
    r"\btonight\b",
    r"\byesterday\b",
    r"\bthis week\b",
    r"\bnext week\b",
    r"\bthis month\b",
    r"\bnext month\b",
    r"\bmonday\b",
    r"\btuesday\b",
    r"\bwednesday\b",
    r"\bthursday\b",
    r"\bfriday\b",
    r"\bsaturday\b",
    r"\bsunday\b",
    r"\bby\s+\w+\b",
    r"\bbefore\s+\w+\b",
    r"\bafter\s+\w+\b"
]


# ============================================================
# PARSE CHAT MESSAGES
# ============================================================

def parse_messages(text):
    """
    Convert chat text into:
    [
        {
            "person": "Arjun",
            "message": "We need to complete..."
        }
    ]
    """

    messages = []

    if not text:
        return messages

    lines = text.splitlines()

    current_person = None
    current_message = []

    for raw_line in lines:

        line = raw_line.strip()

        if not line:
            continue

        # Match:
        # Arjun: Hello
        # Sneha: I'll do this
        match = re.match(
            r"^\s*([^:\n]{1,50})\s*:\s*(.+)$",
            line
        )

        if match:

            # Save previous message
            if current_person is not None:

                messages.append({
                    "person": current_person.strip(),
                    "message": " ".join(current_message).strip()
                })

            current_person = match.group(1).strip()
            current_message = [match.group(2).strip()]

        else:

            # Continuation of previous message
            if current_person is not None:
                current_message.append(line)

    # Save final message
    if current_person is not None:

        messages.append({
            "person": current_person.strip(),
            "message": " ".join(current_message).strip()
        })

    return messages


# ============================================================
# CLEAN TEXT
# ============================================================

def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ============================================================
# SPLIT SENTENCES
# ============================================================

def split_sentences(text):

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text.strip()
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


# ============================================================
# IMPORTANT WORDS
# ============================================================

def important_words(text):

    words = re.findall(
        r"[A-Za-z']+",
        text.lower()
    )

    return [
        word
        for word in words
        if word not in STOP_WORDS
        and len(word) > 2
    ]


# ============================================================
# SENTENCE SCORE
# ============================================================

def sentence_score(sentence, frequencies):

    words = important_words(sentence)

    if not words:
        return 0

    score = sum(
        frequencies.get(word, 0)
        for word in words
    )

    # Give extra importance to action sentences
    for word in words:

        if word in ACTION_VERBS:
            score += 2

    # Give extra importance to deadline sentences
    lower_sentence = sentence.lower()

    for pattern in DEADLINE_PATTERNS:

        if re.search(pattern, lower_sentence):
            score += 2

    return score / max(len(words), 1)


# ============================================================
# EXTRACT SUMMARY
# ============================================================

def extract_summary(messages, max_sentences=3):

    if not messages:
        return ""

    all_text = " ".join(
        message["message"]
        for message in messages
    )

    sentences = split_sentences(all_text)

    if not sentences:
        return ""

    words = important_words(all_text)

    frequencies = Counter(words)

    scored = []

    for index, sentence in enumerate(sentences):

        score = sentence_score(
            sentence,
            frequencies
        )

        scored.append(
            (score, index, sentence)
        )

    # Highest scoring sentences
    selected = sorted(
        scored,
        key=lambda item: item[0],
        reverse=True
    )[:max_sentences]

    # Restore original conversation order
    selected = sorted(
        selected,
        key=lambda item: item[1]
    )

    summary = " ".join(
        item[2]
        for item in selected
    )

    return clean_text(summary)


# ============================================================
# EXTRACT ACTIONS
# ============================================================

def extract_actions(messages):

    actions = []

    for message in messages:

        person = message["person"]
        text = clean_text(message["message"])

        sentences = split_sentences(text)

        for sentence in sentences:

            lower_sentence = sentence.lower()

            has_action = False

            # Check action verbs
            for verb in ACTION_VERBS:

                if re.search(
                    rf"\b{re.escape(verb)}\b",
                    lower_sentence
                ):
                    has_action = True
                    break

            # Also detect common future/action patterns
            if re.search(
                r"\b(i'll|i will|we'll|we will|let's|please)\b",
                lower_sentence
            ):
                has_action = True

            if not has_action:
                continue

            # Remove trailing punctuation
            task = sentence.strip()

            task = re.sub(
                r"\s+",
                " ",
                task
            )

            task = task.rstrip(".!?")

            actions.append({
                "person": person,
                "task": task
            })

    return actions


# ============================================================
# EXTRACT DEADLINES
# ============================================================

def extract_deadlines(messages):

    deadlines = []

    for message in messages:

        person = message["person"]
        text = clean_text(message["message"])

        sentences = split_sentences(text)

        for sentence in sentences:

            lower_sentence = sentence.lower()

            found_deadline = None

            # Specific deadline patterns
            for pattern in DEADLINE_PATTERNS:

                match = re.search(
                    pattern,
                    lower_sentence
                )

                if match:

                    found_deadline = match.group(0)

                    break

            if not found_deadline:
                continue

            # Normalize "by friday" → "friday"
            if found_deadline.startswith("by "):

                found_deadline = found_deadline[3:]

            elif found_deadline.startswith("before "):

                found_deadline = found_deadline[7:]

            elif found_deadline.startswith("after "):

                found_deadline = found_deadline[6:]

            found_deadline = found_deadline.strip()

            # Keep the original sentence as description
            description = sentence.strip()

            description = description.rstrip(".!?")

            deadlines.append({
                "person": person,
                "date": found_deadline,
                "description": description
            })

    return deadlines


# ============================================================
# REMOVE DUPLICATE ACTIONS
# ============================================================

def remove_duplicate_actions(actions):

    unique = []

    seen = set()

    for action in actions:

        key = (
            action.get("person", "").lower(),
            action.get("task", "").lower()
        )

        if key in seen:
            continue

        seen.add(key)

        unique.append(action)

    return unique


# ============================================================
# REMOVE DUPLICATE DEADLINES
# ============================================================

def remove_duplicate_deadlines(deadlines):

    unique = []

    seen = set()

    for deadline in deadlines:

        key = (
            deadline.get("person", "").lower(),
            deadline.get("date", "").lower(),
            deadline.get("description", "").lower()
        )

        if key in seen:
            continue

        seen.add(key)

        unique.append(deadline)

    return unique


# ============================================================
# MAIN SUMMARIZER
# ============================================================

def summarize_text(text):

    if not text or not text.strip():

        return {
            "summary": "",
            "actions": [],
            "deadlines": []
        }

    # ----------------------------------------
    # PARSE MESSAGES
    # ----------------------------------------

    messages = parse_messages(text)

    # ----------------------------------------
    # FALLBACK IF CHAT HAS NO NAMES
    # ----------------------------------------

    if not messages:

        messages = [{
            "person": "Team",
            "message": clean_text(text)
        }]

    # ----------------------------------------
    # SUMMARY
    # ----------------------------------------

    summary = extract_summary(
        messages,
        max_sentences=3
    )

    # ----------------------------------------
    # ACTIONS
    # ----------------------------------------

    actions = extract_actions(messages)

    actions = remove_duplicate_actions(
        actions
    )

    # ----------------------------------------
    # DEADLINES
    # ----------------------------------------

    deadlines = extract_deadlines(messages)

    deadlines = remove_duplicate_deadlines(
        deadlines
    )

    # ----------------------------------------
    # RETURN STRUCTURED RESULT
    # ----------------------------------------

    return {
        "summary": summary,
        "actions": actions,
        "deadlines": deadlines
    }