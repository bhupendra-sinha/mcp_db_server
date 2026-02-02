FORBIDDEN_DDL = ["DROP", "TRUNCATE", "ALTER"]
FORBIDDEN_DML = ["DELETE", "UPDATE", "INSERT"]

def validate_sql(query: str, allow_dml: bool = False):
    """
    Validate SQL query for dangerous operations.
    
    Args:
        query: SQL query string to validate
        allow_dml: If True, allows DELETE/UPDATE/INSERT (for parameterized queries)
                   If False, blocks all write operations (for raw SQL queries)
    """
    upper = query.upper()
    
    # Always block DDL operations
    for keyword in FORBIDDEN_DDL:
        if keyword in upper:
            raise ValueError(f"Forbidden DDL operation: {keyword}")
    
    # Block DML only for raw queries (not for parameterized methods)
    if not allow_dml:
        for keyword in FORBIDDEN_DML:
            if keyword in upper:
                raise ValueError(f"Forbidden DML operation in raw query: {keyword}. Use dedicated tools instead.")
