# QueryMind

AI-powered SQL Query Generator and safe MySQL executor. This project has been upgraded to a **traditional full-stack application** featuring a lightning-fast **FastAPI** backend and a beautifully designed **Vanilla HTML/CSS/JS** frontend with a premium glassmorphism dark-mode aesthetic. 

Type a question in plain English; QueryMind uses Gemini (via Google GenAI + LangChain) to generate a MySQL SELECT query, validates it for safety bounds, and executes it. Results are displayed dynamically in a sleek glass-panel UI.

## Features

- **Full-stack Architecture**: FastAPI backend + Vanilla JS/HTML/CSS frontend.
- **Premium UI**: Glassmorphism aesthetic with micro-animations and dark-mode styling.
- **Natural language to SQL**: Generates SQL using Google GenAI (Gemini) + LangChain.
- **Safety checks**: Restricts to SELECT-only, blocks destructive/unsafe keywords.
- **Query limits**: Auto-adds `LIMIT 100` when missing.
- **Live DB Execution**: Executes on MySQL and renders results asynchronously as HTML tables.

## Tech Stack

- **Backend**: Python 3.14.3, FastAPI, Uvicorn
- **AI Integration**: Google Generative AI (Gemini), LangChain
- **Database**: MySQL (local or remote), mysql-connector-python
- **Frontend**: Vanilla HTML5, CSS3, JavaScript
- **Environment**: python-dotenv

## Project Structure

```text
QueryMind/
├── main.py               # FastAPI server & REST API routes (/api/generate, /api/execute)
├── static/               # Frontend assets
│   ├── index.html        # Main application structure
│   ├── style.css         # Premium glassmorphism styling
│   └── script.js         # API integration and dynamic UI logic
├── query_agent.py        # AI query generator logic
├── db_utils.py           # Database connection & safety checks
├── requirements.txt      # Python dependencies
└── README.md
```

## Getting Started

### 1 Clone and install requirements

```bash
pip install -r requirements.txt
```

### 2 Configure environment

Ensure you have a `.env` file containing the following variables:

```bash
GOOGLE_API_KEY=AIza...
GEMINI_MODEL=gemini-1.5-pro

DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=test
```

### 3 Run the application

Spin up the Uvicorn ASGI server:

```bash
uvicorn main:app --reload
```

Open `http://localhost:8000` in your browser.

## Usage

1. **Configure DB**: Use the left sidebar to enter your local/remote MySQL credentials.
2. **Set Context**: Provide a schema outline in the provided text area to guide the AI.
3. **Prompt Generating**: Type your plain text question in the main search bar (e.g. "List top 3 employees by salary").
4. **Generate**: Click "Generate SQL". The AI will generate a safe query, and the UI will present a safety badge indicating whether the query passed database bounds.
5. **Execute**: Once verified safe, click "Run Query" to retrieve your results in the frontend table.

## Safety Measures

QueryMind strictly enforces read-only access:

- Only `SELECT` (or `WITH`) statements are allowed.
- Multiple statements and destructive keywords (e.g., `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `CREATE`, `TRUNCATE`, `GRANT`, `REVOKE`) are rigorously blocked.
- Potential exfiltration queries (e.g., `INTO OUTFILE`) are blocked.
- A default `LIMIT 100` appended at runtime ensures no system lock-up.

*Always review the generated SQL before executing on a production database.*

## License

MIT
