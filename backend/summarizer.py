from transformers import pipeline
import re


summarizer = pipeline(
    "summarization",
    model="sshleifer/distilbart-cnn-12-6"
)


def clean_conversation(text: str) -> str:
    # Normalize spaces
    text = re.sub(r"\s+", " ", text).strip()

    # Remove speaker names
    text = re.sub(
        r"\b[A-Za-z][A-Za-z0-9 _-]{0,30}:\s*",
        "",
        text
    )

    return text


def summarize_text(text: str) -> str:

    if not text.strip():
        return "Please provide some text to summarize."

    cleaned_text = clean_conversation(text)

    # Keep the original conversation for very short inputs
    words = cleaned_text.split()

    if len(words) < 20:
        return cleaned_text

    cleaned_text = cleaned_text[:5000]

    result = summarizer(
        cleaned_text,
        max_length=80,
        min_length=15,
        do_sample=False
    )

    summary = result[0]["summary_text"]

    summary = re.sub(
        r"\s+",
        " ",
        summary
    ).strip()

    return summary