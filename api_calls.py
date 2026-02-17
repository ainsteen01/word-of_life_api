import os
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pymongo import MongoClient
from dotenv import load_dotenv

# ==============================
# Load environment variables
# ==============================
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI not found in environment variables")

# ==============================
# MongoDB connection
# ==============================
client = MongoClient(MONGO_URI)
db = client["bible_db"]
collection = db["verses"]

# ==============================
# FastAPI app
# ==============================
app = FastAPI(title="Bible API", description="Access Bible verses and chapters")

# ==============================
# Root endpoint (ADD THIS!)
# ==============================
@app.get("/")
async def root():
    return {
        "message": "📖 Bible API is running!",
        "documentation": "/docs",
        "alternative_docs": "/redoc",
        "available_endpoints": {
            "GET /ping": "Check if API is alive",
            "GET /books": "List all Bible books",
            "GET /chapters/{book}": "List chapters for a book (e.g., /chapters/John)",
            "GET /chapter/{book}/{chapter_num}": "Get a specific chapter (e.g., /chapter/John/3)",
            "GET /docs": "Interactive API documentation (Swagger UI)",
            "GET /redoc": "Alternative API documentation"
        }
    }

# ==============================
# Data models (optional, for docs)
# ==============================
class Verse(BaseModel):
    verse: int
    text: str
    textTran: str

class Chapter(BaseModel):
    book: str
    chapter: int
    verses: List[Verse]

# ==============================
# Endpoints
# ==============================

@app.get("/ping")
def ping():
    return {"message": "pong"}


@app.get("/books")
def list_books():
    books = collection.distinct("book")
    return {"books": sorted(books)}


@app.get("/chapters/{book}")
def list_chapters(book: str):
    chapters_cursor = collection.find(
        {"book": book},
        {"_id": 0, "chapter": 1}
    )

    chapters = sorted([doc["chapter"] for doc in chapters_cursor])

    if not chapters:
        raise HTTPException(status_code=404, detail="Book not found")

    return {"chapters": chapters}


@app.get("/chapter/{book}/{chapter_num}")
def get_chapter(book: str, chapter_num: int):
    doc = collection.find_one(
        {"book": book, "chapter": chapter_num},
        {"_id": 0}
    )

    if not doc:
        raise HTTPException(status_code=404, detail="Book or chapter not found")

    return JSONResponse(content=doc)
