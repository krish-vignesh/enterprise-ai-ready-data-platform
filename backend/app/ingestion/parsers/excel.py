import pandas as pd


def parse_excel(input_path, sheet_name=0):
    """Extract one worksheet from an Excel workbook and return it as a pandas DataFrame.

    The sheet_name argument may be either a worksheet name or an index. The
    default value 0 selects the first worksheet.
    """
    return pd.read_excel(input_path, sheet_name=sheet_name)
