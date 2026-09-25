import camelot


def extract_pdf_tables(input_path, pages="all", flavor="lattice"):
    """Extract tables from a text-based PDF using Camelot.

    This parser reads the source PDF, extracts tables from the specified pages,
    and returns a list of pandas DataFrames. The flavor can be selected as
    "lattice" for ruling-line based tables or "stream" for whitespace-based
    tables.
    """
    tables = camelot.read_pdf(input_path, pages=pages, flavor=flavor)

    if not tables:
        return []

    return [table.df for table in tables]
