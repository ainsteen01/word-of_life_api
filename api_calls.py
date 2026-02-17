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
# Fixed endpoints for your data structure
# ==============================

@app.get("/books")
def list_books():
    """List all Bible books"""
    books = collection.distinct("book")
    return {"books": sorted(books)}


@app.get("/chapters/{book}")
def list_chapters(book: str):
    """List all chapters for a specific book"""
    # FIND ALL documents for this book (not just one)
    chapters_cursor = collection.find(
        {"book": book},
        {"_id": 0, "chapters.chapter": 1}
    )
    
    # Convert cursor to list
    docs = list(chapters_cursor)
    
    if not docs:
        raise HTTPException(status_code=404, detail=f"Book '{book}' not found")
    
    # Extract chapter numbers from each document
    chapters = []
    for doc in docs:
        if "chapters" in doc:
            # Handle if chapters is an object with chapter field
            if isinstance(doc["chapters"], dict) and "chapter" in doc["chapters"]:
                chapters.append(doc["chapters"]["chapter"])
            # Handle if chapters is an array
            elif isinstance(doc["chapters"], list):
                for ch in doc["chapters"]:
                    if isinstance(ch, dict) and "chapter" in ch:
                        chapters.append(ch["chapter"])
    
    # Remove duplicates (just in case) and sort
    chapters = sorted(list(set(chapters)))
    
    return {
        "book": book, 
        "chapters": chapters,
        "total_chapters": len(chapters)
    }


@app.get("/chapter/{book}/{chapter_num}")
def get_chapter(book: str, chapter_num: int):
    """Get a specific chapter with all verses"""
    # Find the document that contains this specific chapter
    # This works when each document is one chapter
    doc = collection.find_one(
        {
            "book": book,
            "chapters.chapter": chapter_num
        },
        {"_id": 0}
    )
    
    if not doc:
        # Try alternative structure if above fails
        doc = collection.find_one(
            {"book": book},
            {"_id": 0}
        )
        if doc and "chapters" in doc:
            if isinstance(doc["chapters"], list):
                for ch in doc["chapters"]:
                    if ch.get("chapter") == chapter_num:
                        return {
                            "book": book,
                            "chapter": chapter_num,
                            "verses": ch.get("verses", [])
                        }
        
        raise HTTPException(status_code=404, detail=f"Chapter {chapter_num} not found in {book}")
    
    # Extract the chapter data
    if "chapters" in doc:
        if isinstance(doc["chapters"], dict):
            # Each document contains one chapter
            return {
                "book": book,
                "chapter": doc["chapters"].get("chapter"),
                "verses": doc["chapters"].get("verses", [])
            }
        elif isinstance(doc["chapters"], list):
            for ch in doc["chapters"]:
                if ch.get("chapter") == chapter_num:
                    return {
                        "book": book,
                        "chapter": chapter_num,
                        "verses": ch.get("verses", [])
                    }
    
    # Fallback: return the whole document
    return {
        "book": book,
        "chapter": chapter_num,
        "data": doc
    }


# Debug endpoint to check structure
@app.get("/debug/books")
def debug_books():
    """Debug endpoint to see book structures"""
    books = collection.find({}, {"_id": 0, "book": 1, "chapters.chapter": 1}).limit(10)
    result = []
    for book in books:
        result.append(book)
    return {
        "total_documents": len(result),
        "sample_books": result
    }


# New debug endpoint specifically for Genesis
@app.get("/debug/genesis")
def debug_genesis():
    """Debug endpoint to see all Genesis documents"""
    docs = list(collection.find(
        {"book": "Genesis"},
        {"_id": 0, "book": 1, "chapters.chapter": 1}
    ))
    
    chapters = []
    for doc in docs:
        if "chapters" in doc and isinstance(doc["chapters"], dict):
            chapters.append(doc["chapters"].get("chapter"))
    
    return {
        "book": "Genesis",
        "documents_found": len(docs),
        "chapters_found": sorted(chapters),
        "raw_docs": docs
    }
