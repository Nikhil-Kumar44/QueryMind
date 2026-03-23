import os
from typing import Optional, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from query_agent import generate_sql
from db_utils import validate_sql_safety, execute_select, get_database_schema

load_dotenv()

app = FastAPI(title="QueryMind - AI SQL Generator")

# We'll serve the static directory at /static
# But wait, we want to serve index.html at the root /
# So we'll mount /static and also add a specific route for /

# Create static directory if it doesn't exist (just in case during init)
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

class GenerateRequest(BaseModel):
    user_query: str
    schema_text: str

class ExecuteRequest(BaseModel):
    sql_text: str
    host: str
    port: int
    user: str
    password: str
    database: str

class SchemaRequest(BaseModel):
    host: str
    port: int
    user: str
    password: str
    database: str

@app.get("/")
async def read_index():
    return FileResponse("static/index.html")

@app.post("/api/generate")
async def api_generate(req: GenerateRequest):
    if not req.user_query.strip():
        raise HTTPException(status_code=400, detail="User query cannot be empty")
    
    try:
        sql_text = generate_sql(req.user_query.strip(), req.schema_text.strip())
        safe, reason = validate_sql_safety(sql_text)
        return {
            "sql": sql_text,
            "safe": safe,
            "reason": reason
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/execute")
async def api_execute(req: ExecuteRequest):
    if not req.sql_text.strip():
        raise HTTPException(status_code=400, detail="SQL text cannot be empty")
        
    db_config = {
        "host": req.host,
        "port": req.port,
        "user": req.user,
        "password": req.password,
        "database": req.database
    }
    
    ok, payload = execute_select(req.sql_text, db_config)
    
    if ok:
        return {
            "success": True,
            "rows": len(payload),
            "data": payload
        }
    else:
        return {
            "success": False,
            "error": str(payload)
        }

@app.post("/api/schema")
async def api_schema(req: SchemaRequest):
    db_config = {
        "host": req.host,
        "port": req.port,
        "user": req.user,
        "password": req.password,
        "database": req.database
    }
    
    ok, schema_text = get_database_schema(db_config)
    
    if ok:
        return {"success": True, "schema": schema_text}
    else:
        return {"success": False, "error": schema_text}

