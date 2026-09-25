from pypdf import PdfReader


def parse_pdf(input_path):
    """Extract text from a text-based PDF document and return it as a single string."""
    reader = PdfReader(input_path)
    pages = []

    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)

    return "\n".join(pages)
