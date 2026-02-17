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
collection = db["verses"]  # Your collection name

# ==============================
# FastAPI app
# ==============================
app = FastAPI(title="Bible API", description="Access Bible verses and chapters")

# ==============================
# Root endpoint
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
            "GET /chapters/{book}": "Get all chapters for a book (e.g., /chapters/Genesis)",
            "GET /chapter/{book}/{chapter_num}": "Get a specific chapter (e.g., /chapter/Genesis/1)",
            "GET /docs": "Interactive API documentation (Swagger UI)",
            "GET /redoc": "Alternative API documentation"
        }
    }

@app.get("/ping")
def ping():
    return {"message": "pong"}

# ==============================
# Updated endpoints for your data structure
# ==============================

@app.get("/books")
def list_books():
    """List all Bible books"""
    # Your data has each book as a document with a "book" field
    books = collection.distinct("book")
    return {"books": sorted(books)}


@app.get("/chapters/{book}")
def list_chapters(book: str):
    """List all chapters for a specific book"""
    # Find the book document
    book_doc = collection.find_one(
        {"book": book},
        {"_id": 0, "chapters.chapter": 1}
    )
    
    if not book_doc:
        raise HTTPException(status_code=404, detail=f"Book '{book}' not found")
    
    # Extract chapter numbers from the chapters array/object
    if "chapters" in book_doc:
        # Handle case where chapters might be an array or object
        if isinstance(book_doc["chapters"], list):
            chapters = [ch["chapter"] for ch in book_doc["chapters"]]
        else:
            # Single chapter object (like in your data)
            chapters = [book_doc["chapters"]["chapter"]]
    else:
        chapters = []
    
    return {"book": book, "chapters": sorted(chapters)}


@app.get("/chapter/{book}/{chapter_num}")
def get_chapter(book: str, chapter_num: int):
    """Get a specific chapter with all verses"""
    # Find the book document
    book_doc = collection.find_one(
        {"book": book},
        {"_id": 0}
    )
    
    if not book_doc:
        raise HTTPException(status_code=404, detail=f"Book '{book}' not found")
    
    # Check if chapters exists and is the right format
    if "chapters" not in book_doc:
        raise HTTPException(status_code=404, detail="No chapters found in this book")
    
    # Handle different possible structures
    chapter_data = None
    
    if isinstance(book_doc["chapters"], list):
        # If chapters is an array of chapter objects
        for ch in book_doc["chapters"]:
            if ch.get("chapter") == chapter_num:
                chapter_data = ch
                break
    else:
        # If chapters is a single object (like your Genesis data)
        if book_doc["chapters"].get("chapter") == chapter_num:
            chapter_data = book_doc["chapters"]
    
    if not chapter_data:
        raise HTTPException(status_code=404, detail=f"Chapter {chapter_num} not found in {book}")
    
    # Return the chapter with book name included for clarity
    return {
        "book": book,
        "chapter": chapter_num,
        "verses": chapter_data.get("verses", [])
    }


# Optional: Debug endpoint to check structure
@app.get("/debug/books")
def debug_books():
    """Debug endpoint to see book structures"""
    books = collection.find({}, {"_id": 0, "book": 1, "chapters.chapter": 1}).limit(5)
    result = []
    for book in books:
        result.append(book)
    return {"sample_books": result}
