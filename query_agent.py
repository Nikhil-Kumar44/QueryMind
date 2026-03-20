from __future__ import annotations

import os
import re
from typing import Optional

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv()


SYSTEM_PROMPT = (
    "You are QueryMind, an expert MySQL query generator. "
    "Convert natural language requests into SAFE MySQL SELECT queries only. "
    "Rules:\n"
    "- Output only the SQL inside a fenced code block using ```sql ... ```\n"
    "- Use valid MySQL syntax.\n"
    "- NEVER generate destructive statements (NO INSERT/UPDATE/DELETE/ALTER/DROP/CREATE/REPLACE/TRUNCATE/GRANT/REVOKE).\n"
    "- Do not modify data. Read-only SELECTs only.\n"
    "- Include LIMIT 100 by default unless a smaller LIMIT is explicitly asked.\n"
)


USER_PROMPT = (
    "Database schema:\n{schema}\n\n"
    "User question: {question}\n\n"
    "Return only one SQL statement in a single code block."
)


def _extract_sql_from_markdown(text: str) -> str:
    """Extract first SQL code block; fall back to raw text if none."""
    if not text:
        return ""
    fence = re.search(r"```sql\s*([\s\S]*?)```", text, flags=re.IGNORECASE)
    if fence:
        return fence.group(1).strip()
    inline = re.search(r"```\s*([\s\S]*?)```", text)
    if inline:
        return inline.group(1).strip()
    return text.strip()


def generate_sql(user_query: str, schema: str) -> str:
    """Generate a single MySQL SELECT statement for the provided question and schema."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY not set. Add it to your environment or .env file.")

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("user", USER_PROMPT),
    ])

    model = ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-1.5-pro"),
        temperature=0.2,
        max_tokens=400,
        timeout=60,
    )

    chain = prompt | model
    response = chain.invoke({"schema": schema, "question": user_query})

    text = response.content if hasattr(response, "content") else str(response)
    sql = _extract_sql_from_markdown(text)
    return sql


