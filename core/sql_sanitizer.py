import re

def sanitize_sql(query: str):
    if not query:
        raise ValueError("Empty query")

    # Remove backticks, markdown, etc.
    query = query.strip()
    query = re.sub(r"```sql|```", "", query, flags=re.IGNORECASE).strip()

    # Remove trailing semicolons (safe)
    query = query.rstrip(";")

    q = query.lower()

    # Only allow SELECT
    if not q.startswith("select"):
        raise ValueError("Only SELECT queries allowed")

    # Block dangerous keywords
    forbidden = ["drop", "delete", "insert", "update", "alter", "truncate"]
    if any(word in q for word in forbidden):
        raise ValueError("Dangerous query detected")

    # Block multiple SELECTs
    if q.count("select") > 1:
        raise ValueError("Multiple statements not allowed")

    return query