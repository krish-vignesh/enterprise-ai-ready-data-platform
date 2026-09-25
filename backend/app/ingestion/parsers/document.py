from docx import Document


def parse_document(input_path):
    """Extract text from a DOCX document and return it as a single string."""
    document = Document(input_path)
    paragraphs = []

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if text:
            paragraphs.append(text)

    return "\n".join(paragraphs)
