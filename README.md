# QueryMind

AI-powered SQL Query Generator and safe MySQL executor. Type a question in plain English; QueryMind uses GPT-4 (via OpenAI + LangChain) to generate a MySQL SELECT query, validates it for safety, and executes it. Results are shown in a Streamlit app.

## Features

- Natural language to SQL using GPT-4 + LangChain
- Safety checks: SELECT-only, blocks destructive/unsafe statements
- Auto-adds `LIMIT 100` when missing
- Executes on MySQL and displays results as a table (pandas)
- Clean Streamlit UI

## Tech Stack

- Python 3.10+
- OpenAI API (GPT-4)
- LangChain
- MySQL (local or remote)
- mysql-connector-python
- Streamlit, Pandas
- python-dotenv

## Project Structure

```
QueryMind/
├── app.py                # Streamlit UI
├── query_agent.py        # AI query generator using LangChain + GPT-4
├── db_utils.py           # DB connection + safe query execution
├── .env.example          # Template for environment variables
├── requirements.txt
└── README.md
```

## Getting Started

### 1) Clone and install

```bash
pip install -r requirements.txt
```

### 2) Configure environment

Copy `.env.example` to `.env` and fill in values:

```bash
GEMINI_API_KEY=sk-...
GEMINI_MODEL=gemini-1.5-pro   # or gpt-4o, gpt-4.1, etc.

DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=test
```

### 3) Ensure your MySQL is running

Schema example (optional but recommended to guide the model):

```sql
CREATE TABLE employees (
  id INT PRIMARY KEY,
  name VARCHAR(255),
  dept VARCHAR(255),
  salary INT,
  join_date DATE
);
```

### 4) Run the app

```bash
streamlit run app.py
```

Open the provided URL in your browser.

## Usage

1. Enter your question in natural language.
2. Click "Generate SQL" to see the proposed query and safety verdict.
3. If it passes safety, click "Run Query" to execute on the configured DB.

Example prompts:

- "List top 3 employees by salary."
- "Show average salary by department."

## Safety

QueryMind enforces read-only access:

- Only `SELECT` statements are allowed.
- Multiple statements and destructive keywords (e.g., `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `CREATE`, `REPLACE`, `TRUNCATE`, `GRANT`, `REVOKE`) are blocked.
- Potential exfiltration patterns (e.g., `INTO OUTFILE`) are blocked.
- A default `LIMIT 100` is appended when missing.

Always review the generated SQL before executing.

## Notes

- The model quality depends on the quality of schema context you provide in the sidebar.
- Set `GEMINI_MODEL` in `.env` to your preferred GPT-4 family model.

## License

MIT


