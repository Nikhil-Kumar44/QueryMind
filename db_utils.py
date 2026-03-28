from __future__ import annotations

import re
from typing import Tuple, Union


import mysql.connector


_DESTRUCTIVE_KEYWORDS = [
    r"\bINSERT\b",
    r"\bUPDATE\b",
    r"\bDELETE\b",
    r"\bDROP\b",
    r"\bALTER\b",
    r"\bCREATE\b",
    r"\bTRUNCATE\b",
    r"\bGRANT\b",
    r"\bREVOKE\b",
    r"\bCALL\b",
]


def _strip_sql_comments(sql_text: str) -> str:
    # Remove /* ... */ block comments
    no_block = re.sub(r"/\*[\s\S]*?\*/", " ", sql_text)
    # Remove -- line comments
    no_line = re.sub(r"--.*$", " ", no_block, flags=re.MULTILINE)
    # Remove # line comments (MySQL)
    no_hash = re.sub(r"#.*$", " ", no_line, flags=re.MULTILINE)
    return no_hash


def _strip_string_literals(sql_text: str) -> str:
    """Remove text inside single/double quotes to avoid false semicolon hits."""
    # Replace quoted strings with empty quotes, preserving length isn't needed for our checks
    no_single = re.sub(r"'(?:''|[^'])*'", "''", sql_text)
    no_double = re.sub(r'"(?:""|[^"])*"', '""', no_single)
    return no_double


def _has_multiple_statements(sql_text: str) -> bool:
    # Ignore semicolons inside string literals
    without_strings = _strip_string_literals(sql_text)
    parts = [p.strip() for p in without_strings.split(';') if p.strip()]
    return len(parts) > 1


def is_safe_sql(sql_text: str) -> bool:
    if not sql_text or not sql_text.strip():
        return False

    cleaned = _strip_sql_comments(sql_text).strip()

    # Block multiple statements
    if _has_multiple_statements(cleaned):
        return False

    # Must start with SELECT or WITH (allow leading parentheses/whitespace)
    if not re.match(r"^\s*\(*\s*(SELECT|WITH)\b", cleaned, flags=re.IGNORECASE):
        return False

    # Basic destructive keyword scan (allow functions like REPLACE())
    without_strings = _strip_string_literals(cleaned)
    upper_text = without_strings.upper()
    for kw in _DESTRUCTIVE_KEYWORDS:
        if re.search(kw, upper_text, flags=re.IGNORECASE):
            return False

    # Block INTO OUTFILE / DUMPFILE exfiltration
    if re.search(r"INTO\s+(OUTFILE|DUMPFILE)\b", upper_text, flags=re.IGNORECASE):
        return False

    return True


def validate_sql_safety(sql_text: str) -> Tuple[bool, str]:
    """Return (is_safe, reason). Reason is empty when safe."""
    if not sql_text or not sql_text.strip():
        return False, "Empty SQL."

    cleaned = _strip_sql_comments(sql_text).strip()
    if _has_multiple_statements(cleaned):
        return False, "Multiple statements detected."
    if not re.match(r"^\s*\(*\s*(SELECT|WITH)\b", cleaned, flags=re.IGNORECASE):
        return False, "Only SELECT (or WITH) is allowed."
    without_strings = _strip_string_literals(cleaned)
    upper_text = without_strings.upper()
    for kw in _DESTRUCTIVE_KEYWORDS:
        if re.search(kw, upper_text, flags=re.IGNORECASE):
            return False, "Blocked keyword detected."
    if re.search(r"INTO\s+(OUTFILE|DUMPFILE)\b", upper_text, flags=re.IGNORECASE):
        return False, "INTO OUTFILE/DUMPFILE is not allowed."
    return True, ""


def _ensure_limit(sql_text: str, default_limit: int = 100) -> str:
    # If a LIMIT already present, keep it
    if re.search(r"\bLIMIT\b\s+\d+", sql_text, flags=re.IGNORECASE):
        return sql_text
    # Append LIMIT at the end (before trailing semicolon if any)
    trimmed = sql_text.rstrip().rstrip(";")
    return f"{trimmed} LIMIT {default_limit}"


def execute_select(sql_text: str, db_config: dict) -> Tuple[bool, Union[list, str]]:
    """
    Execute a safe SELECT query against MySQL. Returns (ok, payload).
    - ok=True: payload is a list of dicts representing the rows
    - ok=False: payload is an error message
    """
    try:
        if not is_safe_sql(sql_text):
            return False, "Unsafe or non-SELECT query blocked."

        final_sql = _ensure_limit(sql_text)

        conn = mysql.connector.connect(
            host=db_config.get("host"),
            user=db_config.get("user"),
            password=db_config.get("password"),
            database=db_config.get("database"),
            port=db_config.get("port", 3306),
            autocommit=True,
        )
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(final_sql)
            rows = cursor.fetchall()
        finally:
            conn.close()

        return True, rows
    except Exception as exc:  # noqa: BLE001 - surfacing DB errors directly
        return False, str(exc)

def get_database_schema(db_config: dict) -> Tuple[bool, str]:
    """
    Connect to MySQL and fetch table names and column definitions.
    Returns (True, schema_string) or (False, error_message).
    """
    try:
        conn = mysql.connector.connect(
            host=db_config.get("host"),
            user=db_config.get("user"),
            password=db_config.get("password"),
            database=db_config.get("database"),
            port=db_config.get("port", 3306),
        )
        try:
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall()]
            
            schema_lines = []
            for table in tables:
                cursor.execute(f"DESCRIBE `{table}`")
                columns = cursor.fetchall()
                col_defs = []
                for col in columns:
                    col_name = col[0]
                    col_type = col[1].decode('utf-8') if isinstance(col[1], bytes) else col[1]
                    col_defs.append(f"{col_name} {col_type}")
                schema_lines.append(f"{table}({', '.join(col_defs)})")
        finally:
            conn.close()

        if not schema_lines:
            return True, "No tables found in database."
        return True, "\n".join(schema_lines)
    except Exception as exc:
        return False, str(exc)
