import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


_model = None
_tokenizer = None


def load_ai_model():

    global _model
    global _tokenizer

    if _model is None or _tokenizer is None:

        model_name = "sshleifer/distilbart-cnn-12-6"

        _tokenizer = AutoTokenizer.from_pretrained(
            model_name
        )

        _model = AutoModelForSeq2SeqLM.from_pretrained(
            model_name
        )

        _model.eval()

    return _tokenizer, _model


def generate_summary(text):

    if not text or not text.strip():
        raise ValueError(
            "No text available for AI analysis."
        )

    text = text.strip()

    tokenizer, model = load_ai_model()

    max_input_characters = 3000

    chunks = []

    for start in range(
        0,
        len(text),
        max_input_characters
    ):

        chunk = text[
            start:start + max_input_characters
        ].strip()

        if len(chunk) >= 50:
            chunks.append(chunk)

    if not chunks:
        raise ValueError(
            "Text is too short for AI summarization."
        )

    summaries = []

    for chunk in chunks:

        inputs = tokenizer(
            chunk,
            return_tensors="pt",
            max_length=1024,
            truncation=True
        )

        with torch.no_grad():

            summary_ids = model.generate(
                **inputs,
                max_length=180,
                min_length=40,
                num_beams=4,
                early_stopping=True
            )

        summary = tokenizer.decode(
            summary_ids[0],
            skip_special_tokens=True
        )

        if summary.strip():
            summaries.append(
                summary.strip()
            )

    if not summaries:
        raise ValueError(
            "AI could not generate a summary."
        )

    return " ".join(summaries)


def detect_document_type(text):

    text_lower = text.lower()

    if any(
        word in text_lower
        for word in [
            "invoice",
            "total amount",
            "bill to",
            "invoice number"
        ]
    ):
        return "Invoice / Bill"

    if any(
        word in text_lower
        for word in [
            "resume",
            "curriculum vitae",
            "work experience",
            "education",
            "skills"
        ]
    ):
        return "Resume / CV"

    if any(
        word in text_lower
        for word in [
            "contract",
            "agreement",
            "terms and conditions",
            "party"
        ]
    ):
        return "Contract / Agreement"

    if any(
        word in text_lower
        for word in [
            "report",
            "findings",
            "conclusion",
            "analysis"
        ]
    ):
        return "Report"

    if any(
        word in text_lower
        for word in [
            "application",
            "applicant",
            "application form"
        ]
    ):
        return "Application / Form"

    return "General Document"


def extract_key_points(text):

    if not text or not text.strip():
        return []

    sentences = []

    for line in text.splitlines():

        line = line.strip()

        if len(line) >= 40:

            cleaned = line.replace(
                "\t",
                " "
            )

            sentences.append(
                cleaned
            )

    key_points = []

    for sentence in sentences:

        if sentence not in key_points:

            key_points.append(
                sentence
            )

        if len(key_points) >= 8:
            break

    return key_points


def analyze_document(text):

    if not text or not text.strip():
        raise ValueError(
            "No document text available."
        )

    summary = generate_summary(text)

    document_type = detect_document_type(
        text
    )

    key_points = extract_key_points(
        text
    )

    word_count = len(
        text.split()
    )

    character_count = len(
        text
    )

    return {
        "summary": summary,
        "document_type": document_type,
        "key_points": key_points,
        "word_count": word_count,
        "character_count": character_count
    }


def summarize_text(text):

    return generate_summary(text)