from delimiters import DATA_START, DATA_END, ROW_START, ROW_END, COL_DELIM

def store_table_data(table_rows):
    """
    Encode table rows into a single delimited string
    """
    encoded = DATA_START
    for row in table_rows:
        encoded += ROW_START + COL_DELIM.join(row) + ROW_END
    encoded += DATA_END
    return encoded


def read_table_data(encoded_data):
    """
    Decode delimited string back into table rows
    """
    content = encoded_data.replace(DATA_START, "").replace(DATA_END, "")
    rows = []

    for r in content.split(ROW_END):
        if ROW_START in r:
            rows.append(
                r.replace(ROW_START, "").split(COL_DELIM)
            )

    return rows