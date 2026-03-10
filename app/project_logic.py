PROJECT_TOKEN = "{PROJECT_NO}"

def normalize_with_project(table_rows, project_no):
    """
    Replace explicit project number with placeholder BEFORE storing
    """
    if not project_no:
        raise ValueError("Project number must be provided")

    normalized_rows = []
    for row in table_rows:
        normalized_rows.append(
            [cell.replace(project_no, PROJECT_TOKEN) for cell in row]
        )

    return normalized_rows


def denormalize_with_project(table_rows, project_no):
    """
    Replace placeholder with actual project number AFTER retrieval
    """
    if not project_no:
        return table_rows

    denormalized_rows = []
    for row in table_rows:
        denormalized_rows.append(
            [cell.replace(PROJECT_TOKEN, project_no) for cell in row]
        )

    return denormalized_rows
