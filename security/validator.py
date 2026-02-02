FORBIDDEN = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER"]

def validate_sql(query: str):
    upper = query.upper()
    for keyword in FORBIDDEN:
        if keyword in upper:
            raise ValueError(f"Forbidden operation: {keyword}")
