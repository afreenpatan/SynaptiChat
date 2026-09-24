import re
from collections import Counter


# ---------------------------------------------------------
# BASIC TEXT SETTINGS
# ---------------------------------------------------------

STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "if", "then",
    "is", "are", "was", "were", "be", "been", "being",
    "to", "of", "in", "on", "at", "for", "from", "with",
    "by", "as", "this", "that", "these", "those",
    "it", "its", "i", "we", "you", "he", "she", "they",
    "me", "my", "our", "your", "their", "will", "would",
    "can", "could", "should", "have", "has", "had",
    "do", "does", "did", "please", "let", "us"
}


ACTION_VERBS = {
    "finish", "complete", "prepare", "create", "make",
    "send", "share", "submit", "review", "check",
    "update", "upload", "download", "write", "design",
    "develop", "build", "test", "fix", "present",
    "discuss", "collect", "analyze", "analyse", "provide",
    "finalize", "finalise", "organize", "organise",
    "call", "meet", "work", "prepare", "give"
}


TIME_PATTERNS = [
    r"\btoday\b",
    r"\btomorrow\b",
    r"\btonight\b",
    r"\byesterday\b",
    r"\bthis week\b",
    r"\bnext week\b",
    r"\bthis month\b",
    r"\bnext month\b",
    r"\bthis weekend\b",
    r"\bnext weekend\b",
    r"\bby\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
    r"\b(on|by)\s+\d{1,2}(st|nd|rd|th)?\b",
    r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",
    r"\b\d{1,2}-\d{1,2}-\d{2,4}\b",
    r"\b(in|within)\s+\d+\s+(day|days|week|weeks|month|months)\b",
    r"\bby\s+\d{1,2}\s*(am|pm)\b",
    r"\bat\s+\d{1,2}\s*(am|pm)\b"
]


# ---------------------------------------------------------
# TEXT CLEANING
# ---------------------------------------------------------

def clean_message(text):
    """
    Cleans one individual message without removing line breaks.
    """

    text = text.replace("\r", "")
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


# ---------------------------------------------------------
# MESSAGE PARSING
# ---------------------------------------------------------

def parse_messages(text):
    """
    Converts chat text into:
    [
        {
            "name": "Arjun",
            "message": "We need to finish..."
        }
    ]

    Supports formats such as:
    Arjun: Hello
    Sneha: I'll prepare the report
    """

    messages = []

    lines = text.splitlines()

    current_name = None
    current_message = []

    for raw_line in lines:

        line = clean_message(raw_line)

        if not line:
            continue

        # Speaker format:
        # Arjun: message
        match = re.match(
            r"^\s*([A-Za-z][A-Za-z0-9 _.-]{0,40})\s*:\s*(.+)$",
            line
        )

        if match:

            # Save previous message
            if current_name is not None and current_message:

                messages.append({
                    "name": current_name.strip(),
                    "message": " ".join(current_message).strip()
                })

            current_name = match.group(1).strip()
            current_message = [match.group(2).strip()]

        else:

            # Continuation of previous message
            if current_name is not None:
                current_message.append(line)

            else:
                # If there is no speaker, treat as Team
                messages.append({
                    "name": "Team",
                    "message": line
                })

    # Save final message
    if current_name is not None and current_message:

        messages.append({
            "name": current_name.strip(),
            "message": " ".join(current_message).strip()
        })

    return messages


# ---------------------------------------------------------
# WORD PROCESSING
# ---------------------------------------------------------

def get_words(text):
    words = re.findall(r"\b[a-zA-Z]{2,}\b", text.lower())

    return [
        word
        for word in words
        if word not in STOP_WORDS
    ]


def split_sentences(text):
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


# ---------------------------------------------------------
# SUMMARY GENERATION
# ---------------------------------------------------------

def generate_summary(messages, max_sentences=3):
    """
    Generates an extractive summary.

    Important:
    Speaker names are preserved separately.
    """

    all_sentences = []

    for message in messages:

        sentences = split_sentences(message["message"])

        for sentence in sentences:

            all_sentences.append({
                "name": message["name"],
                "sentence": sentence
            })

    if not all_sentences:
        return ""

    # Frequency of meaningful words
    all_words = []

    for item in all_sentences:
        all_words.extend(get_words(item["sentence"]))

    frequency = Counter(all_words)

    # Score each sentence
    scored = []

    for index, item in enumerate(all_sentences):

        words = get_words(item["sentence"])

        if not words:
            score = 0
        else:
            score = sum(
                frequency[word]
                for word in words
            ) / len(words)

        # Give action-oriented sentences a small boost
        if any(
            re.search(
                rf"\b{re.escape(verb)}\b",
                item["sentence"].lower()
            )
            for verb in ACTION_VERBS
        ):
            score += 1.5

        scored.append({
            "index": index,
            "name": item["name"],
            "sentence": item["sentence"],
            "score": score
        })

    # Highest scoring sentences
    scored_sorted = sorted(
        scored,
        key=lambda x: x["score"],
        reverse=True
    )

    selected = scored_sorted[:max_sentences]

    # Keep original conversation order
    selected.sort(key=lambda x: x["index"])

    summary_parts = []

    for item in selected:
        summary_parts.append(item["sentence"])

    return " ".join(summary_parts)


# ---------------------------------------------------------
# DEADLINE DETECTION
# ---------------------------------------------------------

def find_deadline(text):
    """
    Finds an actual time/date expression.

    Returns:
        "this week"
        "Friday"
        "tomorrow"
        "tonight"
        etc.

    Returns None if no real deadline/time expression exists.
    """

    text_lower = text.lower()

    # More specific patterns first
    patterns = [
        r"\bthis week\b",
        r"\bnext week\b",
        r"\bthis month\b",
        r"\bnext month\b",
        r"\bthis weekend\b",
        r"\bnext weekend\b",
        r"\btonight\b",
        r"\btomorrow\b",
        r"\btoday\b",
        r"\byesterday\b",
        r"\bby\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
        r"\b(on|by)\s+\d{1,2}(st|nd|rd|th)?\b",
        r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",
        r"\b\d{1,2}-\d{1,2}-\d{2,4}\b",
        r"\b(in|within)\s+\d+\s+(day|days|week|weeks|month|months)\b",
        r"\bby\s+\d{1,2}\s*(am|pm)\b",
        r"\bat\s+\d{1,2}\s*(am|pm)\b"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text_lower,
            re.IGNORECASE
        )

        if match:

            deadline = match.group(0)

            # Clean "by " / "on " when appropriate
            deadline = re.sub(
                r"^(by|on)\s+",
                "",
                deadline,
                flags=re.IGNORECASE
            )

            return deadline.strip()

    # Simple weekday detection
    weekdays = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday"
    ]

    for day in weekdays:

        if re.search(
            rf"\b{day}\b",
            text_lower
        ):
            return day

    return None


# ---------------------------------------------------------
# ACTION DETECTION
# ---------------------------------------------------------

def is_action_message(text):
    """
    Determines whether a message contains a meaningful action.
    """

    text_lower = text.lower()

    # "I'll prepare..."
    if re.search(
        r"\b(i['’]ll|i will|we['’]ll|we will)\b",
        text_lower
    ):
        return True

    # "Please send..."
    if re.search(
        r"\bplease\s+\w+",
        text_lower
    ):
        return True

    # "Let's review..."
    if re.search(
        r"\blet['’]s\s+\w+",
        text_lower
    ):
        return True

    # Explicit action verbs
    for verb in ACTION_VERBS:

        if re.search(
            rf"\b{re.escape(verb)}\b",
            text_lower
        ):
            return True

    return False


# ---------------------------------------------------------
# ACTION CLEANING
# ---------------------------------------------------------

def clean_action_text(text):
    """
    Removes conversational prefixes while preserving
    the actual task.
    """

    cleaned = text.strip()

    # Remove "I'll"
    cleaned = re.sub(
        r"^(i['’]ll|i will)\s+",
        "",
        cleaned,
        flags=re.IGNORECASE
    )

    # Remove "We'll"
    cleaned = re.sub(
        r"^(we['’]ll|we will)\s+",
        "",
        cleaned,
        flags=re.IGNORECASE
    )

    # Remove "Let's"
    cleaned = re.sub(
        r"^let['’]s\s+",
        "",
        cleaned,
        flags=re.IGNORECASE
    )

    # Remove "Please"
    cleaned = re.sub(
        r"^please\s+",
        "",
        cleaned,
        flags=re.IGNORECASE
    )

    return cleaned.strip()


# ---------------------------------------------------------
# EXTRACT ACTIONS
# ---------------------------------------------------------

def extract_actions(messages):
    actions = []

    for message in messages:

        text = message["message"]

        if not is_action_message(text):
            continue

        # Don't treat pure deadline statements as actions
        cleaned = clean_action_text(text)

        if not cleaned:
            continue

        # Remove ending punctuation
        cleaned = cleaned.rstrip(".!?")

        actions.append({
            "name": message["name"],
            "task": cleaned
        })

    return actions


# ---------------------------------------------------------
# EXTRACT DEADLINES
# ---------------------------------------------------------

def extract_deadlines(messages):
    deadlines = []

    for message in messages:

        text = message["message"]

        deadline = find_deadline(text)

        if not deadline:
            continue

        # Remove the deadline phrase from the sentence
        description = re.sub(
            re.escape(deadline),
            "",
            text,
            flags=re.IGNORECASE
        ).strip()

        # Clean common connecting words
        description = re.sub(
            r"\b(by|on|for)\s*$",
            "",
            description,
            flags=re.IGNORECASE
        ).strip()

        description = description.rstrip(".!?")

        # Avoid meaningless deadline entries
        if not description:
            description = "Task"

        deadlines.append({
            "name": message["name"],
            "deadline": deadline,
            "description": description
        })

    return deadlines


# ---------------------------------------------------------
# STRUCTURED RESULT
# ---------------------------------------------------------

def create_structured_summary(text):

    messages = parse_messages(text)

    if not messages:
        return {
            "summary": "",
            "actions": [],
            "deadlines": []
        }

    summary = generate_summary(
        messages,
        max_sentences=3
    )

    actions = extract_actions(messages)

    deadlines = extract_deadlines(messages)

    return {
        "summary": summary,
        "actions": actions,
        "deadlines": deadlines
    }


# ---------------------------------------------------------
# MAIN FUNCTION USED BY FASTAPI
# ---------------------------------------------------------

def summarize_text(text):

    if not text or not text.strip():

        return {
            "summary": "",
            "actions": [],
            "deadlines": []
        }

    # IMPORTANT:
    # Do NOT call clean_message(text) here.
    # We need the original line breaks so that
    # each speaker can be detected separately.

    return create_structured_summary(text)