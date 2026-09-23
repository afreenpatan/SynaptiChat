from transformers import pipeline
import re


# ============================================================
# SYNAPTICHAT - AI CHAT SUMMARIZER
# ============================================================

summarizer = pipeline(
    "summarization",
    model="sshleifer/distilbart-cnn-12-6"
)


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([.,!?])", r"\1", text)
    return text.strip()


# ============================================================
# PARSE CHAT MESSAGES
# Example:
#
# Afreen: I will prepare the introduction tomorrow.
# Priya: I will finish the architecture by Thursday.
#
# ============================================================

def parse_messages(text):

    pattern = r'([A-Za-z][A-Za-z0-9 _-]{0,30})\s*:\s*'

    matches = list(re.finditer(pattern, text))

    messages = []

    for i, match in enumerate(matches):

        speaker = match.group(1).strip()

        start = match.end()

        if i + 1 < len(matches):
            end = matches[i + 1].start()
        else:
            end = len(text)

        message = text[start:end].strip()

        message = clean_text(message)

        if message:

            messages.append({
                "speaker": speaker,
                "message": message
            })

    return messages


# ============================================================
# AI SUMMARY
# ============================================================

def generate_summary(text):

    words = len(text.split())

    # Very short text does not need AI summarization.
    if words < 25:
        return text

    if words <= 80:

        max_length = 45
        min_length = 12

    elif words <= 160:

        max_length = 65
        min_length = 18

    else:

        max_length = min(120, int(words * 0.40))
        min_length = max(20, int(words * 0.15))

    if min_length >= max_length:
        min_length = max(10, max_length - 10)

    try:

        result = summarizer(
            text,
            max_length=max_length,
            min_length=min_length,
            num_beams=4,
            no_repeat_ngram_size=3,
            length_penalty=1.5,
            early_stopping=True
        )

        summary = result[0]["summary_text"]

        return clean_text(summary)

    except Exception as e:

        print("AI summary error:", str(e))

        return clean_text(text)


# ============================================================
# ACTION VERBS
# ============================================================

ACTION_VERBS = [

    "prepare",
    "create",
    "complete",
    "finish",
    "handle",
    "develop",
    "design",
    "write",
    "submit",
    "review",
    "explain",
    "present",
    "organize",
    "finalize",
    "share",
    "work on",
    "build",
    "update",
    "test",
    "implement",
    "document",
    "analyze"

]


# ============================================================
# DEADLINE WORDS
# ============================================================

DAYS = [

    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday"

]

TIME_WORDS = [

    "today",
    "tomorrow",
    "tonight",
    "next week",
    "this week"

]


# ============================================================
# FIND DEADLINE
# ============================================================

def find_deadline(text):

    lower = text.lower()

    # Check days.
    for day in DAYS:

        if re.search(
            r"\b" + day + r"\b",
            lower
        ):

            return day.capitalize()

    # Check relative dates.
    for word in TIME_WORDS:

        pattern = r"\b" + word.replace(
            " ",
            r"\s+"
        ) + r"\b"

        if re.search(
            pattern,
            lower
        ):

            return word.capitalize()

    return None


# ============================================================
# CHECK WHETHER MESSAGE IS AN ACTION
# ============================================================

def is_action_message(message):

    lower = message.lower().strip()

    # --------------------------------------------------------
    # Greetings and simple conversational statements
    # --------------------------------------------------------

    simple_non_actions = [

        r"^hi\b",
        r"^hello\b",
        r"^hey\b",
        r"^thanks\b",
        r"^thank you\b",
        r"^great\b",
        r"^perfect\b",
        r"^okay\b",
        r"^ok\b",
        r"^sure\b"

    ]

    for pattern in simple_non_actions:

        if re.search(
            pattern,
            lower
        ):

            # Example:
            # "Great, I'll finish the architecture."
            # This IS still an action.
            if re.search(
                r"\b(i will|i'll|i can|i am going to|i'm going to)\b",
                lower
            ):

                return True

            return False

    # --------------------------------------------------------
    # Meeting-only statements
    # --------------------------------------------------------

    meeting_only_patterns = [

        r"^let'?s meet\b",
        r"^let us meet\b",
        r"^we should meet\b",
        r"^we will meet\b",
        r"^we'll meet\b"

    ]

    for pattern in meeting_only_patterns:

        if re.search(
            pattern,
            lower
        ):

            return False

    # --------------------------------------------------------
    # Personal commitments
    # --------------------------------------------------------

    commitment_patterns = [

        r"\bi will\b",
        r"\bi'll\b",
        r"\bi can\b",
        r"\bi am going to\b",
        r"\bi'm going to\b"

    ]

    for pattern in commitment_patterns:

        if re.search(
            pattern,
            lower
        ):

            return True

    # --------------------------------------------------------
    # Action verbs
    # --------------------------------------------------------

    for verb in ACTION_VERBS:

        if re.search(
            r"\b" + re.escape(verb) + r"\b",
            lower
        ):

            # A sentence containing "meet" should not
            # automatically become an action.
            if (
                re.search(r"\bmeet\b", lower)
                and not re.search(
                    r"\b(review|prepare|create|finish|complete|"
                    r"explain|present|submit|share)\b",
                    lower
                )
            ):

                return False

            return True

    return False


# ============================================================
# REMOVE ACTION PREFIX
# ============================================================

def remove_action_prefix(text):

    text = re.sub(
        r"^(great|perfect|okay|ok|sure|yes|alright)[,.]?\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"^(I will|I'll|I can|I am going to|I'm going to)\s+",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"^(we will|we'll|we can)\s+",
        "",
        text,
        flags=re.IGNORECASE
    )

    return text.strip()


# ============================================================
# REMOVE DEADLINE FROM ACTION
# ============================================================

def remove_deadline_from_action(text):

    # Example:
    #
    # "finish the architecture by Thursday"
    #
    # becomes:
    #
    # "finish the architecture"

    pattern = (
        r"\s+(?:by|on|before|until)\s+"
        r"(?:today|tomorrow|tonight|next week|this week|"
        r"monday|tuesday|wednesday|thursday|friday|saturday|sunday)"
        r"(?:\s+(?:morning|afternoon|evening|night))?"
        r".*$"
    )

    text = re.sub(
        pattern,
        "",
        text,
        flags=re.IGNORECASE
    )

    return text.strip()


# ============================================================
# CLEAN ACTION
# ============================================================

def clean_action(message):

    text = clean_text(message)

    text = remove_action_prefix(text)

    text = remove_deadline_from_action(text)

    text = text.rstrip(".!?")

    return text.strip()


# ============================================================
# EXTRACT KEY ACTIONS
# ============================================================

def extract_actions(messages):

    actions = []

    seen = set()

    for item in messages:

        speaker = item["speaker"]

        message = clean_text(
            item["message"]
        )

        # Check whether this is an actual action.
        if not is_action_message(message):

            continue

        task = clean_action(message)

        if not task:

            continue

        # Ignore extremely short tasks.
        if len(task.split()) < 2:

            continue

        # Ignore generic statements.
        generic_tasks = [

            "everything",
            "the work",
            "the project",
            "the presentation",
            "it",
            "this"

        ]

        if task.lower() in generic_tasks:

            continue

        # Remove duplicate actions.
        key = (
            speaker.lower().strip(),
            task.lower().strip()
        )

        if key in seen:

            continue

        seen.add(key)

        actions.append({
            "person": speaker,
            "task": task
        })

    return actions


# ============================================================
# CLEAN DEADLINE DESCRIPTION
# ============================================================

def clean_deadline_description(message):

    text = clean_text(message)

    # Remove common openings.
    text = re.sub(
        r"^(great|perfect|okay|ok|sure|yes)[,.]?\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    # --------------------------------------------------------
    # Handle:
    #
    # "I'll share the introduction draft tomorrow."
    #
    # -> "share the introduction draft"
    # --------------------------------------------------------

    text = re.sub(
        r"^(I will|I'll|I can|I'm going to|I am going to)\s+",
        "",
        text,
        flags=re.IGNORECASE
    )

    # --------------------------------------------------------
    # Handle:
    #
    # "Let's meet Friday morning and review the presentation."
    #
    # -> "review the presentation"
    # --------------------------------------------------------

    meeting_pattern = (
        r"^(let'?s|let us)\s+meet\s+"
        r"(today|tomorrow|tonight|next week|this week|"
        r"monday|tuesday|wednesday|thursday|friday|saturday|sunday)"
        r"(?:\s+(?:morning|afternoon|evening|night))?"
        r"\s*(?:and\s+)?"
    )

    text = re.sub(
        meeting_pattern,
        "",
        text,
        flags=re.IGNORECASE
    )

    # --------------------------------------------------------
    # Remove "by Thursday", "on Friday", etc.
    # --------------------------------------------------------

    deadline_pattern = (
        r"\s+(?:by|on|before|until)\s+"
        r"(?:today|tomorrow|tonight|next week|this week|"
        r"monday|tuesday|wednesday|thursday|friday|saturday|sunday)"
        r"(?:\s+(?:morning|afternoon|evening|night))?"
        r".*$"
    )

    text = re.sub(
        deadline_pattern,
        "",
        text,
        flags=re.IGNORECASE
    )

    # Remove standalone relative dates.
    text = re.sub(
        r"\s+(?:today|tomorrow|tonight)\b",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = text.rstrip(".!?")

    return text.strip()


# ============================================================
# EXTRACT DEADLINES
# ============================================================

def extract_deadlines(messages):

    deadlines = []

    seen = set()

    for item in messages:

        speaker = item["speaker"]

        message = clean_text(
            item["message"]
        )

        deadline = find_deadline(message)

        if not deadline:

            continue

        description = clean_deadline_description(
            message
        )

        if not description:

            continue

        # Avoid exact duplicates.
        key = (
            deadline.lower(),
            description.lower()
        )

        if key in seen:

            continue

        seen.add(key)

        deadlines.append({
            "date": deadline,
            "description": description,
            "speaker": speaker
        })

    return deadlines


# ============================================================
# CREATE CLEAN STRUCTURED SUMMARY
# ============================================================

def create_structured_summary(
    messages,
    actions,
    deadlines
):

    if not actions:

        return None

    topics = []

    for action in actions:

        task = action["task"].strip()

        # Remove action verbs.
        topic = re.sub(
            r"^(prepare|create|complete|finish|handle|develop|"
            r"design|write|submit|review|explain|present|organize|"
            r"finalize|share|work on|build|update|test|implement|"
            r"document|analyze)\s+",
            "",
            task,
            flags=re.IGNORECASE
        )

        topic = topic.strip()

        if not topic:
            continue

        # Avoid duplicate topics.
        if topic.lower() not in [
            existing.lower()
            for existing in topics
        ]:

            topics.append(topic)

    if not topics:

        return None

    # --------------------------------------------------------
    # One topic
    # --------------------------------------------------------

    if len(topics) == 1:

        return (
            "The team is working on "
            + topics[0].lower()
            + "."
        )

    # --------------------------------------------------------
    # Two topics
    # --------------------------------------------------------

    if len(topics) == 2:

        return (
            "The team is working on "
            + topics[0].lower()
            + " and "
            + topics[1].lower()
            + "."
        )

    # --------------------------------------------------------
    # More than two topics.
    #
    # Keep the summary concise.
    # --------------------------------------------------------

    selected_topics = topics[:3]

    return (
        "The team is preparing the project presentation, "
        "covering "
        + ", ".join(
            topic.lower()
            for topic in selected_topics[:-1]
        )
        + " and "
        + selected_topics[-1].lower()
        + "."
    )


# ============================================================
# MAIN SUMMARIZATION FUNCTION
# ============================================================

def summarize_text(text):

    if not text or not text.strip():

        return {
            "summary": "",
            "actions": [],
            "deadlines": []
        }

    # Limit extremely large conversations.
    text = text[:12000]

    # --------------------------------------------------------
    # Parse messages.
    # --------------------------------------------------------

    messages = parse_messages(text)

    # --------------------------------------------------------
    # If no speaker names are detected.
    # --------------------------------------------------------

    if not messages:

        cleaned = clean_text(text)

        summary = generate_summary(cleaned)

        return {
            "summary": summary,
            "actions": [],
            "deadlines": []
        }

    # --------------------------------------------------------
    # Extract structured information.
    # --------------------------------------------------------

    actions = extract_actions(messages)

    deadlines = extract_deadlines(messages)

    # --------------------------------------------------------
    # Create clean summary.
    # --------------------------------------------------------

    structured_summary = create_structured_summary(
        messages,
        actions,
        deadlines
    )

    # --------------------------------------------------------
    # Use structured summary when possible.
    # --------------------------------------------------------

    if structured_summary:

        summary = structured_summary

    else:

        conversation = " ".join(
            item["message"]
            for item in messages
        )

        conversation = clean_text(
            conversation
        )

        summary = generate_summary(
            conversation
        )

    # --------------------------------------------------------
    # Final structured response.
    # --------------------------------------------------------

    return {
        "summary": summary,
        "actions": actions,
        "deadlines": deadlines
    }