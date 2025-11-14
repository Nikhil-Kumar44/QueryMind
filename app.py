import os
from typing import Optional, Tuple

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from query_agent import generate_sql
from db_utils import is_safe_sql, validate_sql_safety, execute_select


load_dotenv()


def get_db_config() -> dict:
    return {
        "host": os.getenv("DB_HOST", "127.0.0.1"),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
        "database": os.getenv("DB_NAME", "test"),
        "port": int(os.getenv("DB_PORT", "3306")),
    }


DEFAULT_SCHEMA = (
    "employees(id INT, name VARCHAR(255), dept VARCHAR(255), salary INT, join_date DATE)"
)

EXAMPLES = [
    "List top 3 employees by salary.",
    "Show average salary by department.",
]


def init_state():
    if "generated_sql" not in st.session_state:
        st.session_state.generated_sql = ""
    if "safety_verdict" not in st.session_state:
        st.session_state.safety_verdict = None
    if "safety_reason" not in st.session_state:
        st.session_state.safety_reason = ""


def main():
    st.set_page_config(page_title="QueryMind - AI SQL Generator", layout="wide")
    init_state()

    st.title("QueryMind 🧠🔎")
    st.caption("AI-powered SQL generator and safe executor for MySQL")

    with st.sidebar:
        st.subheader("Database Config")
        cfg = get_db_config()
        st.text_input("Host", value=cfg["host"], key="db_host")
        st.number_input("Port", value=cfg["port"], key="db_port")
        st.text_input("User", value=cfg["user"], key="db_user")
        st.text_input("Password", value=cfg["password"], type="password", key="db_password")
        st.text_input("Database", value=cfg["database"], key="db_name")

        st.divider()
        st.subheader("Schema (guide for the AI)")
        schema_text = st.text_area(
            "Provide the relevant table schemas (read-only)",
            value=DEFAULT_SCHEMA,
            height=150,
        )

        st.divider()
        st.subheader("Examples")
        for ex in EXAMPLES:
            if st.button(ex, use_container_width=True):
                st.session_state.user_query = ex

    user_query = st.text_input(
        "Ask a question in plain English",
        key="user_query",
        placeholder="e.g., Show average salary by department",
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Generate SQL", type="primary"):
            if not user_query.strip():
                st.warning("Please enter a question.")
            else:
                with st.spinner("Generating SQL with GPT-4..."):
                    sql_text = generate_sql(user_query.strip(), schema_text.strip())
                st.session_state.generated_sql = sql_text
                safe, reason = validate_sql_safety(sql_text)
                st.session_state.safety_verdict = safe
                st.session_state.safety_reason = reason

    with col2:
        run_clicked = st.button("Run Query", disabled=not st.session_state.generated_sql)

    st.subheader("Generated SQL")
    if st.session_state.generated_sql:
        st.code(st.session_state.generated_sql, language="sql")
    else:
        st.write("No SQL generated yet.")

    if st.session_state.safety_verdict is not None:
        if st.session_state.safety_verdict:
            st.success("Safety check: PASS (SELECT-only)")
        else:
            msg = "Safety check: FAIL"
            if st.session_state.safety_reason:
                msg += f" — {st.session_state.safety_reason}"
            st.error(msg)

    if run_clicked:
        if not st.session_state.safety_verdict:
            st.error("Blocked: Query is not safe to execute.")
        else:
            db_cfg = {
                "host": st.session_state.db_host,
                "port": int(st.session_state.db_port),
                "user": st.session_state.db_user,
                "password": st.session_state.db_password,
                "database": st.session_state.db_name,
            }
            with st.spinner("Executing on MySQL..."):
                ok, payload = execute_select(st.session_state.generated_sql, db_cfg)
            if ok:
                df: pd.DataFrame = payload
                if df.empty:
                    st.info("Query executed successfully, but returned no rows.")
                else:
                    st.dataframe(df, use_container_width=True)
                    st.caption(f"Returned {len(df)} rows")
            else:
                st.error("Execution error:")
                st.code(str(payload))


if __name__ == "__main__":
    main()


