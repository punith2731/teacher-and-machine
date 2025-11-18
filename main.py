
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import os
import json
import google.generativeai as genai

DB_PATH = os.getenv("DB_PATH", "aemr_books.db")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

app = FastAPI(title="Student Chapter System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS mcq_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                unit_id INTEGER,
                question TEXT,
                option_a TEXT,
                option_b TEXT,
                option_c TEXT,
                option_d TEXT,
                correct_answer TEXT
            );
            """
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print("DB init error:", e)

init_db()

class Unit(BaseModel):
    unit_id: int
    document_id: int
    title: str
    start_page: int
    end_page: int

class Page(BaseModel):
    id: int
    document_id: int
    page_number: int
    content: str

class MCQ(BaseModel):
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str

@app.get("/units")
def list_units():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT unit_id, document_id, title, start_page, end_page FROM units")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.get("/unit-pages/{unit_id}")
def get_unit_pages(unit_id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT document_id, start_page, end_page FROM units WHERE unit_id=?", (unit_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Unit not found")
    document_id = row["document_id"]
    start_page = row["start_page"]
    end_page = row["end_page"]
    cur.execute(
        """
        SELECT id, document_id, page_number, content
        FROM pages
        WHERE document_id=? AND page_number BETWEEN ? AND ?
        ORDER BY page_number ASC
        """,
        (document_id, start_page, end_page),
    )
    pages = cur.fetchall()
    conn.close()
    return [dict(p) for p in pages]

def get_unit_text(unit_id: int) -> str:
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT document_id, start_page, end_page FROM units WHERE unit_id=?", (unit_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Unit not found")
    document_id = row["document_id"]
    start_page = row["start_page"]
    end_page = row["end_page"]
    cur.execute(
        """
        SELECT content
        FROM pages
        WHERE document_id=? AND page_number BETWEEN ? AND ?
        ORDER BY page_number ASC
        """,
        (document_id, start_page, end_page),
    )
    texts = [r["content"] for r in cur.fetchall()]
    conn.close()
    return "\n".join(texts)

def parse_mcq_response(text: str):
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```", 2)
        if len(cleaned) >= 2:
            cleaned = cleaned[1]
        else:
            cleaned = cleaned[0]
        cleaned = cleaned.replace("json", "", 1).strip()
    data = json.loads(cleaned)
    if isinstance(data, dict):
        if "mcqs" in data and isinstance(data["mcqs"], list):
            return data["mcqs"]
        else:
            return [data]
    return data

@app.get("/generate-mcq/{unit_id}")
def generate_mcq(unit_id: int):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not set")
    chapter_text = get_unit_text(unit_id)
    if not chapter_text.strip():
        raise HTTPException(status_code=400, detail="No text found for this unit")
    prompt = f"""
Read the chapter text below and generate 10 MCQ questions.
Return ONLY a JSON array, no extra text. Example:

[
  {{
    "question": "....",
    "option_a": "....",
    "option_b": "....",
    "option_c": "....",
    "option_d": "....",
    "correct_answer": "A"
  }}
]

Chapter Text:
{chapter_text}
"""
    model = genai.GenerativeModel("gemini-pro")
    resp = model.generate_content(prompt)
    try:
        mcqs = parse_mcq_response(resp.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse MCQ JSON: {e}")
    conn = get_db()
    cur = conn.cursor()
    for q in mcqs:
        try:
            cur.execute(
                """
                INSERT INTO mcq_questions
                (unit_id, question, option_a, option_b, option_c, option_d, correct_answer)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    unit_id,
                    q.get("question", ""),
                    q.get("option_a", ""),
                    q.get("option_b", ""),
                    q.get("option_c", ""),
                    q.get("option_d", ""),
                    q.get("correct_answer", ""),
                ),
            )
        except Exception as e:
            print("Insert MCQ error:", e)
    conn.commit()
    conn.close()
    return {"status": "ok", "count": len(mcqs), "mcqs": mcqs}

@app.get("/chapter-audio/{unit_id}")
def chapter_audio(unit_id: int):
    text = get_unit_text(unit_id)
    return {"unit_id": unit_id, "text": text}

@app.get("/health")
def health():
    return {"status": "ok"}
